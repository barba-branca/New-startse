from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .services import RFQService
import json

@login_required
@csrf_exempt
def request_quote(request):
    """
    API view to request an OTC quote.
    """
    if request.method != "POST":
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
        base_asset = data.get('asset', 'BTC').upper()
        volume = float(data.get('volume', 0))
        side = data.get('side', 'BUY').upper()
        
        if volume <= 0:
            return JsonResponse({'error': 'Volume invalid'}, status=status)
            
        quote = RFQService.create_quote(request.user, base_asset, volume, side)
        
        return JsonResponse({
            'quote_id': quote.id,
            'price': float(quote.price_final),
            'total_brl': float(quote.price_final * quote.volume),
            'expires_at': quote.expires_at.isoformat(),
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@csrf_exempt
def execute_trade(request):
    """
    API view to execute a previously generated quote.
    """
    if request.method != "POST":
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
        quote_id = data.get('quote_id')
        
        trade = RFQService.execute_trade(quote_id, request.user)
        
        return JsonResponse({
            'trade_id': trade.id,
            'status': 'executed',
            'amount': float(trade.total_quote),
            'timestamp': trade.executed_at.isoformat()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
