import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('apps')


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'success': False,
            'message': 'An error occurred.',
            'errors': response.data,
            'status_code': response.status_code,
        }
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                error_data['message'] = str(response.data['detail'])
        elif isinstance(response.data, list):
            error_data['message'] = 'Validation error.'
            error_data['errors'] = response.data

        response.data = error_data
    else:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        response = Response({
            'success': False,
            'message': 'Internal server error.',
            'status_code': 500,
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
