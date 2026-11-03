import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import AIConversation, AIMessage
from .engine import process_assistant_query


@ensure_csrf_cookie
def assistant_page_view(request):
    """
    Dedicated PerkCart AI Assistant page with conversation history,
    suggested query prompt chips, and interactive chat interface.
    """
    conversation = None
    messages_history = []

    if request.user.is_authenticated:
        conversation, _ = AIConversation.objects.get_or_create(
            user=request.user,
            defaults={'title': f"Shopping Chat ({request.user.first_name or request.user.username})"}
        )
        messages_history = conversation.messages.all()[:30]
    else:
        # Session-based guest conversation
        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key
        conversation, _ = AIConversation.objects.get_or_create(
            session_key=session_key,
            user=None,
            defaults={'title': f"Guest Chat ({session_key[:6]})"}
        )
        messages_history = conversation.messages.all()[:30]

    suggested_prompts = [
        "Find enterprise laptops under ₹1,00,000",
        "Compare PerkBook Ultra 16 Pro and ThinkPro X1",
        "What are the active corporate coupon codes?",
        "How does employee verification work on PerkCart?",
        "What should I do if I see error CART-001?",
        "What is the status of my recent orders?",
    ]

    return render(request, 'assistant/assistant.html', {
        'conversation': conversation,
        'messages_history': messages_history,
        'suggested_prompts': suggested_prompts,
    })


@require_POST
def assistant_api_view(request):
    """
    AJAX endpoint:
    - Receives user prompt
    - Executes retrieval and AI generation (or search fallback)
    - Records conversation and messages in DB
    - Returns JSON response with markdown content, engine badge, and sources
    """
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
    except (ValueError, KeyError):
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON body.'}, status=400)

    if not query:
        return JsonResponse({'status': 'error', 'message': 'Prompt cannot be empty.'}, status=400)

    # Input length constraint
    if len(query) > 500:
        return JsonResponse({'status': 'error', 'message': 'Prompt exceeds maximum allowable length (500 chars).'}, status=400)

    # Resolve or create conversation
    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key or ""
    if not session_key and not user:
        request.session.save()
        session_key = request.session.session_key

    if user:
        conversation, _ = AIConversation.objects.get_or_create(
            user=user,
            defaults={'title': query[:50]}
        )
    else:
        conversation, _ = AIConversation.objects.get_or_create(
            session_key=session_key,
            user=None,
            defaults={'title': query[:50]}
        )

    # Record User Message
    AIMessage.objects.create(
        conversation=conversation,
        role='user',
        content=query,
    )

    # Process query
    result = process_assistant_query(query, user=user, session_key=session_key)

    # Record Assistant Message
    AIMessage.objects.create(
        conversation=conversation,
        role='assistant',
        content=result['content'],
        engine_used=result['engine'],
        retrieved_sources=result['sources']
    )

    return JsonResponse({
        'status': 'success',
        'content': result['content'],
        'engine': result['engine'],
        'sources': result['sources']
    })


@require_POST
def clear_history_view(request):
    """
    Clears the current user's AI conversation history.
    """
    if request.user.is_authenticated:
        AIConversation.objects.filter(user=request.user).delete()
    elif request.session.session_key:
        AIConversation.objects.filter(session_key=request.session.session_key).delete()

    return JsonResponse({'status': 'success', 'message': 'Conversation history cleared.'})
