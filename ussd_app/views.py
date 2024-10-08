from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# In-memory session store
sessions = {}

@csrf_exempt
def ussd_view(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON request body
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Extract necessary USSD fields from the request
        ussd_id = data.get('USERID', '')
        msisdn = data.get('MSISDN', '')
        user_data = data.get('USERDATA', '')
        msgtype = data.get('MSGTYPE', True)  # True if first request, False if subsequent
        session_id = data.get('SESSIONID', '')

        if not session_id:
            return JsonResponse({'error': 'SESSIONID is missing'}, status=400)

        # Retrieve or create session
        if session_id not in sessions:
            sessions[session_id] = {'screen': 1, 'feeling': '', 'reason': ''}

        session = sessions[session_id]

        # Initial request (first screen)
        if msgtype:
            msg = f"Welcome to {ussd_id} USSD Application.\nHow are you feeling?\n\n1. Feeling fine.\n2. Feeling frisky.\n3. Not well."
            session['screen'] = 1  # First screen
            response_data = {
                "USERID": ussd_id,
                "MSISDN": msisdn,
                "USERDATA": user_data,
                "SESSIONID": session_id,
                "MSG": msg,
                "MSGTYPE": True  # Keep the session open
            }

        else:
            # Handle user input based on the current screen
            if session['screen'] == 1:
                if user_data == '1':
                    session['feeling'] = 'Feeling fine'
                elif user_data == '2':
                    session['feeling'] = 'Feeling frisky'
                elif user_data == '3':
                    session['feeling'] = 'Not well'
                else:
                    # Invalid input, repeat Screen 1
                    msg = "Invalid input. How are you feeling?\n1. Feeling fine\n2. Feeling frisky\n3. Not well"
                    response_data = {
                        "USERID": ussd_id,
                        "MSISDN": msisdn,
                        "USERDATA": user_data,
                        "SESSIONID": session_id,
                        "MSG": msg,
                        "MSGTYPE": True
                    }
                    return JsonResponse(response_data)

                # Move to Screen 2
                msg = f"Why are you {session['feeling']}?\n1. Money issues\n2. Relationship\n3. A lot"
                session['screen'] = 2  # Set to second screen
                response_data = {
                    "USERID": ussd_id,
                    "MSISDN": msisdn,
                    "USERDATA": user_data,
                    "SESSIONID": session_id,
                    "MSG": msg,
                    "MSGTYPE": True
                }

            elif session['screen'] == 2:
                # Process second screen options
                if user_data == '1':
                    session['reason'] = 'because of money'
                elif user_data == '2':
                    session['reason'] = 'because of relationship'
                elif user_data == '3':
                    session['reason'] = 'because of a lot'
                else:
                    # Invalid input, repeat Screen 2
                    msg = f"Invalid input. Why are you {session['feeling']}?\n1. Money issues\n2. Relationship\n3. A lot"
                    response_data = {
                        "USERID": ussd_id,
                        "MSISDN": msisdn,
                        "USERDATA": user_data,
                        "SESSIONID": session_id,
                        "MSG": msg,
                        "MSGTYPE": True
                    }
                    return JsonResponse(response_data)

                # Screen 3: Final message
                msg = f"You are {session['feeling']} {session['reason']}."
                response_data = {
                    "USERID": ussd_id,
                    "MSISDN": msisdn,
                    "USERDATA": user_data,
                    "SESSIONID": session_id,
                    "MSG": msg,
                    "MSGTYPE": False  # End the session
                }

                # End the session
                del sessions[session_id]

        return JsonResponse(response_data)

    return JsonResponse({'error': 'Method not allowed'}, status=405)
