"""
NFL Picker Web Application
Flask-based web interface for NFL team analysis and predictions
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from nfl_picker.config import NFL_TEAMS
from nfl_picker.database import NFLDatabase
from nfl_picker.stats_database import NFLStatsDatabase
from nfl_picker.utils import get_current_nfl_week
from nfl_picker.focused_analysis import FocusedTeamAnalysis

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Initialize databases with error handling
try:
    db = NFLDatabase()
    stats_db = NFLStatsDatabase()
except Exception as e:
    print(f"Warning: Database initialization error: {e}")
    db = None
    stats_db = None


@app.before_request
def before_request():
    """Set content type for API routes."""
    if request.path.startswith('/api/'):
        # Ensure API routes return JSON
        pass  # Flask will handle this via jsonify


@app.after_request
def after_request(response):
    """Ensure API routes have correct content type."""
    if request.path.startswith('/api/'):
        response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/')
def index():
    """Main page with team analysis interface."""
    return render_template('index.html', teams=NFL_TEAMS)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render."""
    try:
        # Check if databases are initialized
        db_status = "ok" if db is not None else "error"
        stats_db_status = "ok" if stats_db is not None else "error"
        
        # Check API keys
        import os
        openai_key = "set" if os.getenv('OPENAI_API_KEY') else "missing"
        serper_key = "set" if os.getenv('SERPER_API_KEY') else "missing"
        
        return jsonify({
            'status': 'healthy',
            'databases': {
                'main_db': db_status,
                'stats_db': stats_db_status
            },
            'api_keys': {
                'openai': openai_key,
                'serper': serper_key
            }
        }), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


@app.route('/api/test', methods=['GET'])
def test_api():
    """Test endpoint to verify API is working."""
    return jsonify({
        'status': 'ok',
        'message': 'API is working',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/teams', methods=['GET'])
def get_teams():
    """Get list of all NFL teams."""
    return jsonify({'teams': NFL_TEAMS})


@app.route('/api/team-stats', methods=['GET'])
def get_team_stats():
    """Get statistics for selected teams."""
    if stats_db is None:
        return jsonify({'error': 'Stats database not initialized'}), 500
    
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    week = request.args.get('week', type=int) or get_current_nfl_week()
    season = request.args.get('season', type=int, default=2025)
    
    if not team1 and not team2:
        return jsonify({'error': 'At least one team required'}), 400
    
    try:
        stats = {}
        if team1:
            team1_stats = stats_db.get_team_stats(team1, week, season)
            stats[team1] = format_team_stats(team1_stats)
        
        if team2:
            team2_stats = stats_db.get_team_stats(team2, week, season)
            stats[team2] = format_team_stats(team2_stats)
        
        return jsonify({'stats': stats, 'week': week, 'season': season})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_teams():
    """Run analysis for two teams."""
    try:
        # Check if databases are initialized
        if db is None or stats_db is None:
            return jsonify({'error': 'Database not initialized. Please check server logs.'}), 500
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Invalid JSON in request body'}), 400
        
        team1 = data.get('team1')
        team2 = data.get('team2')
        include_injuries = data.get('include_injuries', True)
        include_coaching = data.get('include_coaching', True)
        include_special_teams = data.get('include_special_teams', True)
        
        if not team1 or not team2:
            return jsonify({'error': 'Both teams required'}), 400
        
        if team1 == team2:
            return jsonify({'error': 'Teams must be different'}), 400
        
        # Run analysis
        print(f"Starting analysis for {team1} vs {team2}")
        home_team = team2  # Team 2 is always home team
        
        try:
            print("Creating FocusedTeamAnalysis instance...")
            analysis = FocusedTeamAnalysis(
                team1=team1,
                team2=team2,
                home_team=home_team,
                include_injuries=include_injuries,
                include_coaching=include_coaching,
                include_special_teams=include_special_teams
            )
            print("FocusedTeamAnalysis created, running analysis...")
            print("Note: Analysis may take 1-3 minutes. Please be patient...")
            
            # Run analysis (Gunicorn timeout will handle long-running requests)
            # Note: Render free tier has 30-second timeout, but Gunicorn is set to 300 seconds
            results = analysis.run_analysis()
            print("Analysis completed successfully")
                
        except TimeoutError as timeout_err:
            print(f"Timeout during analysis: {timeout_err}")
            return jsonify({
                'error': str(timeout_err),
                'suggestion': 'Analysis timed out. Render free tier has a 30-second request timeout. The analysis may need more time. Please try again or consider upgrading your Render plan.'
            }), 504
        except MemoryError as mem_err:
            print(f"Memory error during analysis: {mem_err}")
            return jsonify({
                'error': 'Analysis failed due to insufficient memory',
                'suggestion': 'The analysis requires more memory than available. Consider reducing the number of analysis options or upgrading your Render plan.'
            }), 507
        except Exception as analysis_error:
            print(f"Error during analysis: {analysis_error}")
            traceback.print_exc()
            raise  # Re-raise to be caught by outer try/except
        
        # Get team statistics
        week = get_current_nfl_week()
        season = 2025
        
        try:
            team1_stats = stats_db.get_team_stats(team1, week, season)
            team2_stats = stats_db.get_team_stats(team2, week, season)
            results['team1_stats'] = format_team_stats(team1_stats)
            results['team2_stats'] = format_team_stats(team2_stats)
        except Exception as e:
            print(f"Error getting team stats: {e}")
        
        # Save prediction to database
        try:
            save_prediction_to_db(results, week)
        except Exception as e:
            print(f"Error saving prediction: {e}")
        
        return jsonify({'success': True, 'results': results})
        
    except Exception as e:
        error_msg = str(e)
        traceback.print_exc()
        # Ensure we always return JSON
        return jsonify({'error': error_msg, 'type': type(e).__name__}), 500


@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """Get list of predictions."""
    if db is None:
        return jsonify({'error': 'Database not initialized'}), 500
    
    try:
        predictions = db.get_predictions()
        prediction_list = []
        for pred in predictions:
            game_id, team1, team2, winner, date = pred
            prediction_list.append({
                'game_id': game_id,
                'team1': team1,
                'team2': team2,
                'predicted_winner': winner,
                'date': date
            })
        return jsonify({'predictions': prediction_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/accuracy', methods=['GET'])
def get_accuracy():
    """Get prediction accuracy statistics."""
    if db is None:
        return jsonify({'error': 'Database not initialized'}), 500
    
    try:
        stats = db.get_accuracy_stats()
        if not stats or stats[0] == 0:
            return jsonify({
                'total': 0,
                'correct': 0,
                'accuracy_rate': 0,
                'avg_confidence': 0,
                'avg_score_diff': 0
            })
        
        total, correct, avg_conf, avg_diff = stats
        accuracy_rate = (correct / total) * 100 if total > 0 else 0
        
        recent_games = db.get_recent_games_with_results(limit=10)
        games = []
        for game in recent_games:
            team1, team2, pred_winner, conf, actual_winner, home_score, away_score, correct, diff = game
            games.append({
                'team1': team1,
                'team2': team2,
                'predicted_winner': pred_winner,
                'confidence': conf,
                'actual_winner': actual_winner,
                'home_score': home_score,
                'away_score': away_score,
                'correct': bool(correct),
                'score_difference': diff
            })
        
        return jsonify({
            'total': total,
            'correct': correct,
            'accuracy_rate': round(accuracy_rate, 1),
            'avg_confidence': round(avg_conf, 2),
            'avg_score_diff': round(avg_diff, 1),
            'recent_games': games
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/save-result', methods=['POST'])
def save_result():
    """Save actual game result."""
    if db is None:
        return jsonify({'error': 'Database not initialized'}), 500
    
    data = request.get_json()
    
    game_id = data.get('game_id')
    home_score = data.get('home_score')
    away_score = data.get('away_score')
    game_date = data.get('game_date')
    weather = data.get('weather')
    
    if not game_id or home_score is None or away_score is None:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Determine actual winner
        if home_score > away_score:
            actual_winner = db.get_team_from_prediction(game_id, 'home_team')
        elif away_score > home_score:
            team1 = db.get_team_from_prediction(game_id, 'team1')
            team2 = db.get_team_from_prediction(game_id, 'team2')
            home_team = db.get_team_from_prediction(game_id, 'home_team')
            actual_winner = team2 if team1 == home_team else team1
        else:
            actual_winner = "Tie"
        
        week = get_current_nfl_week()
        season = 2025
        
        db.save_game_result(
            game_id=game_id,
            team1=db.get_team_from_prediction(game_id, 'team1'),
            team2=db.get_team_from_prediction(game_id, 'team2'),
            home_team=db.get_team_from_prediction(game_id, 'home_team'),
            actual_winner=actual_winner,
            actual_score_home=home_score,
            actual_score_away=away_score,
            game_date=game_date,
            weather_conditions=weather,
            week=week,
            season=season
        )
        
        db.calculate_and_store_accuracy(game_id)
        
        return jsonify({'success': True, 'message': 'Game result saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def format_team_stats(team_stats):
    """Format team statistics for display."""
    formatted = {}
    for position, players in team_stats.items():
        if players:
            top_player = players[0]
            formatted[position] = {
                'player_name': top_player.get('player_name', 'N/A'),
                'stats': {k: v for k, v in top_player.items() if k not in ['id', 'player_id', 'player_name', 'team', 'position', 'week', 'season', 'last_updated', 'data_source']}
            }
    return formatted


def save_prediction_to_db(results, week):
    """Save prediction to database."""
    if db is None:
        print("Warning: Cannot save prediction - database not initialized")
        return
    
    import re
    
    team1_clean = results['team1'].replace(" ", "_").replace(".", "")
    team2_clean = results['team2'].replace(" ", "_").replace(".", "")
    game_id = f"{team1_clean}_vs_{team2_clean}_Week_{week:02d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    predicted_winner = results['predicted_winner']
    predicted_score = results['predicted_score']
    
    # Parse predicted score
    try:
        numbers = re.findall(r'\d+', predicted_score)
        if len(numbers) >= 2:
            home_score = int(numbers[0])
            away_score = int(numbers[1])
        else:
            home_score = away_score = 0
    except:
        home_score = away_score = 0
    
    # Extract confidence
    confidence = 0.75
    if 'confidence' in results:
        try:
            conf_text = str(results['confidence'])
            conf_match = re.search(r'(\d+)%', conf_text)
            if conf_match:
                confidence = float(conf_match.group(1)) / 100
        except:
            pass
    
    try:
        db.save_prediction(
            game_id=game_id,
            team1=results['team1'],
            team2=results['team2'],
            home_team=results['home_team'],
            predicted_winner=predicted_winner,
            predicted_score_home=home_score,
            predicted_score_away=away_score,
            confidence_level=confidence,
            analysis_data=results,
            week=week,
            season=2025
        )
    except Exception as e:
        print(f"Error saving prediction to database: {e}")


@app.errorhandler(404)
def not_found(error):
    # Check if it's an API request
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found'}), 404
    return render_template('index.html', teams=NFL_TEAMS), 404


@app.errorhandler(500)
def internal_error(error):
    # Check if it's an API request
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error', 'message': str(error)}), 500
    return render_template('index.html', teams=NFL_TEAMS), 500


@app.errorhandler(Exception)
def handle_exception(e):
    # Check if it's an API request
    if request.path.startswith('/api/'):
        traceback.print_exc()
        return jsonify({'error': str(e), 'type': type(e).__name__}), 500
    # For non-API requests, return the error page
    traceback.print_exc()
    return render_template('index.html', teams=NFL_TEAMS), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

