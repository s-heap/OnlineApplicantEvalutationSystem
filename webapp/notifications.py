from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

def createNotification(type, message):
    '''
    Creates a notification in the system which will be displayed when the next page is loaded.

    :param type: The type of message to be displayed, either success or an error.
    :param message: The text of the message to be created in the notification.
    '''
    if 'notifications' not in session.keys():
        session['notifications'] = []
    session['notifications'].append({"type": type, "message": message})
