import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('apps')


def _extract_message(data) -> str:
    """Pull the most human-readable message from DRF error data."""
    if isinstance(data, dict):
        # Prefer 'detail' (authentication errors, etc.)
        if 'detail' in data:
            return str(data['detail'])
        # Non-field validation errors
        if 'non_field_errors' in data:
            msgs = data['non_field_errors']
            return msgs[0] if msgs else 'Validation error.'
        # First field error
        for key, val in data.items():
            msgs = val if isinstance(val, list) else [val]
            if msgs:
                field_label = key.replace('_', ' ').capitalize()
                return f'{field_label}: {msgs[0]}'
    if isinstance(data, list) and data:
        return str(data[0])
    return 'An error occurred.'


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        message = _extract_message(response.data)
        error_data = {
            'success': False,
            'message': message,
            'errors': response.data if isinstance(response.data, (dict, list)) else None,
            'status_code': response.status_code,
        }
        response.data = error_data
    else:
        logger.error(f'Unhandled exception: {exc}', exc_info=True)
        response = Response({
            'success': False,
            'message': 'Internal server error.',
            'errors': None,
            'status_code': 500,
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
