import functions_framework
from flask import jsonify

@functions_framework.http
def chuck_norris_jokes(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    jokes = [
        {"id": 1, "joke": "Chuck Norris counted to infinity. Twice."},
        {"id": 2, "joke": "Chuck Norris can slam a revolving door."},
        {"id": 3, "joke": "Chuck Norris once kicked a horse in the chin. Its descendants are known today as Giraffes."},
        {"id": 4, "joke": "Chuck Norris doesn't wear a watch. He decides what time it is."},
        {"id": 5, "joke": "The original title for Alien vs. Predator was Alien and Predator vs. Chuck Norris. The film was cancelled because no one would pay to see a movie 14 seconds long."}
    ]
    
    return jsonify({
        "status": "success",
        "data": jokes,
        "source": "The legend itself"
    })
