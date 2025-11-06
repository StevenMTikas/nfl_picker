// API Base URL
const API_BASE = '';

// Run analysis
async function runAnalysis() {
    const team1 = document.getElementById('team1').value;
    const team2 = document.getElementById('team2').value;
    const includeInjuries = document.getElementById('include_injuries').checked;
    const includeCoaching = document.getElementById('include_coaching').checked;
    const includeSpecialTeams = document.getElementById('include_special_teams').checked;

    if (!team1 || !team2) {
        alert('Please select both teams');
        return;
    }

    if (team1 === team2) {
        alert('Please select two different teams');
        return;
    }

    // Show loading
    document.getElementById('loading').style.display = 'flex';
    document.getElementById('analyze-btn').disabled = true;

    try {
        const response = await fetch(`${API_BASE}/api/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                team1: team1,
                team2: team2,
                include_injuries: includeInjuries,
                include_coaching: includeCoaching,
                include_special_teams: includeSpecialTeams
            })
        });

        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            throw new Error(`Server returned non-JSON response. Status: ${response.status}. Response: ${text.substring(0, 200)}`);
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Analysis failed');
        }

        displayResults(data.results);
        loadTeamStats(team1, team2);

    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'Failed to run analysis. Please check server logs.');
    } finally {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('analyze-btn').disabled = false;
    }
}

// Display analysis results
function displayResults(results) {
    const resultsSection = document.getElementById('results-section');
    const resultsContent = document.getElementById('results-content');

    let html = `
        <div class="prediction-box">
            <h3>🎯 Prediction</h3>
            <div class="prediction-item">
                <strong>Predicted Winner:</strong> ${results.predicted_winner}
            </div>
            <div class="prediction-item">
                <strong>Predicted Score:</strong> ${results.predicted_score}
            </div>
            <div class="prediction-item">
                <strong>Confidence:</strong> ${results.confidence}
            </div>
            <div class="prediction-item">
                <strong>Analysis Date:</strong> ${results.analysis_date}
            </div>
        </div>

        <div class="key-factors-section">
            <h3>Key Factors</h3>
            <ul class="key-factors">
                ${results.key_factors.map(factor => `<li>${factor}</li>`).join('')}
            </ul>
        </div>

        <div class="detailed-analysis">
            <h3>Detailed Analysis</h3>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; white-space: pre-wrap; font-family: monospace; font-size: 0.9rem; max-height: 500px; overflow-y: auto;">
                ${results.detailed_analysis}
            </div>
        </div>
    `;

    resultsContent.innerHTML = html;
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Load team statistics
async function loadTeamStats(team1, team2) {
    try {
        const response = await fetch(`${API_BASE}/api/team-stats?team1=${encodeURIComponent(team1)}&team2=${encodeURIComponent(team2)}`);
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            console.error('Team stats: Non-JSON response received');
            return;
        }
        
        const data = await response.json();

        if (response.ok && data.stats) {
            displayTeamStats(data.stats);
        }
    } catch (error) {
        console.error('Error loading team stats:', error);
    }
}

// Display team statistics
function displayTeamStats(stats) {
    const statsSection = document.getElementById('stats-section');
    const statsContent = document.getElementById('stats-content');

    let html = '<div class="stats-grid">';
    
    for (const [teamName, teamData] of Object.entries(stats)) {
        html += `<div class="stat-card">
            <h4>${teamName}</h4>`;
        
        for (const [position, data] of Object.entries(teamData)) {
            if (data && data.player_name) {
                html += `<div class="stat-item">
                    <strong>${position}:</strong> ${data.player_name}
                </div>`;
            }
        }
        
        html += `</div>`;
    }
    
    html += '</div>';
    statsContent.innerHTML = html;
    statsSection.style.display = 'block';
}

// Load accuracy statistics
async function loadAccuracy() {
    const content = document.getElementById('accuracy-content');
    content.innerHTML = '<p>Loading...</p>';

    try {
        const response = await fetch(`${API_BASE}/api/accuracy`);
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            throw new Error(`Server returned non-JSON response: ${text.substring(0, 200)}`);
        }
        
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to load accuracy');
        }

        if (data.total === 0) {
            content.innerHTML = '<p>No accuracy data available yet. Enter some game results to see learning progress.</p>';
            return;
        }

        let html = `
            <div class="prediction-box" style="margin-top: 20px;">
                <h3>Overall Statistics</h3>
                <div class="prediction-item">
                    <strong>Total Predictions:</strong> ${data.total}
                </div>
                <div class="prediction-item">
                    <strong>Correct Predictions:</strong> ${data.correct}
                </div>
                <div class="prediction-item">
                    <strong>Accuracy Rate:</strong> ${data.accuracy_rate}%
                </div>
                <div class="prediction-item">
                    <strong>Average Confidence:</strong> ${data.avg_confidence}
                </div>
                <div class="prediction-item">
                    <strong>Average Score Difference:</strong> ${data.avg_score_diff} points
                </div>
            </div>
        `;

        if (data.recent_games && data.recent_games.length > 0) {
            html += '<h3 style="margin-top: 30px;">Recent Game Results</h3>';
            html += '<div class="stats-grid">';
            
            data.recent_games.forEach(game => {
                const icon = game.correct ? '✓' : '✗';
                const color = game.correct ? 'green' : 'red';
                html += `
                    <div class="stat-card">
                        <div style="font-size: 1.5rem; color: ${color}; margin-bottom: 10px;">${icon}</div>
                        <div class="stat-item"><strong>${game.team1} vs ${game.team2}</strong></div>
                        <div class="stat-item">Predicted: ${game.predicted_winner} (${game.confidence.toFixed(1)})</div>
                        <div class="stat-item">Actual: ${game.actual_winner} (${game.home_score}-${game.away_score})</div>
                        <div class="stat-item">Score Diff: ${game.score_difference} pts</div>
                    </div>
                `;
            });
            
            html += '</div>';
        }

        content.innerHTML = html;

    } catch (error) {
        content.innerHTML = `<div class="error">Error loading accuracy data: ${error.message}</div>`;
    }
}

// Show error message
function showError(message) {
    const resultsContent = document.getElementById('results-content');
    resultsContent.innerHTML = `<div class="error">${message}</div>`;
    document.getElementById('results-section').style.display = 'block';
}

// Auto-refresh stats when teams are selected
document.getElementById('team1').addEventListener('change', function() {
    const team1 = this.value;
    const team2 = document.getElementById('team2').value;
    if (team1 && team2) {
        loadTeamStats(team1, team2);
    }
});

document.getElementById('team2').addEventListener('change', function() {
    const team1 = document.getElementById('team1').value;
    const team2 = this.value;
    if (team1 && team2) {
        loadTeamStats(team1, team2);
    }
});

