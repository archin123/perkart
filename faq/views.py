from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from .models import FAQ, FAQCategory, FAQVote, UnansweredQuestion


def faq_list_view(request):
    """
    Searchable, filterable accordion FAQ page with category chips,
    helpful/unhelpful feedback, and an unanswered question submission form.
    """
    category_slug = request.GET.get('category', '')
    query = request.GET.get('q', '').strip()

    categories = FAQCategory.objects.all().order_by('order')
    faqs = FAQ.objects.filter(is_active=True).select_related('category')
    selected_category = None

    if category_slug:
        selected_category = get_object_or_404(FAQCategory, slug=category_slug)
        faqs = faqs.filter(category=selected_category)

    if query:
        faqs = faqs.filter(
            Q(question__icontains=query) |
            Q(answer__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Handle Unanswered Question submission
    if request.method == 'POST' and 'submit_question' in request.POST:
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        question = request.POST.get('question', '').strip()

        if name and email and question:
            UnansweredQuestion.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name,
                email=email,
                company_name=company_name,
                question=question,
            )
            messages.success(
                request,
                "Thank you! Your question has been submitted to the PerkCart Support & Knowledge Team. We will review and update the FAQ repository."
            )
            return redirect('faq:faq_list')
        else:
            messages.error(request, "Please fill in your name, email, and the question.")

    return render(request, 'faq/faq_list.html', {
        'faqs': faqs,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
        'total_faqs': faqs.count(),
    })


def faq_vote_view(request, faq_id):
    """
    AJAX endpoint for helpful/unhelpful voting with duplicate protection.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

    faq = get_object_or_404(FAQ, id=faq_id)
    vote_type = request.POST.get('vote_type', '').lower()

    if vote_type not in ('helpful', 'unhelpful'):
        return JsonResponse({'status': 'error', 'message': 'Invalid vote type.'}, status=400)

    # Ensure session key exists
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key

    # Check if this session already voted
    existing_vote = FAQVote.objects.filter(faq=faq, session_key=session_key).first()

    if existing_vote:
        if existing_vote.vote_type == vote_type:
            return JsonResponse({
                'status': 'already_voted',
                'message': 'You have already submitted this feedback.',
                'helpful_count': faq.helpful_count,
                'unhelpful_count': faq.unhelpful_count,
            })
        else:
            # Change vote
            if existing_vote.vote_type == 'helpful':
                faq.helpful_count = max(0, faq.helpful_count - 1)
                faq.unhelpful_count += 1
            else:
                faq.unhelpful_count = max(0, faq.unhelpful_count - 1)
                faq.helpful_count += 1
            existing_vote.vote_type = vote_type
            existing_vote.save()
            faq.save()
    else:
        # New vote
        FAQVote.objects.create(faq=faq, session_key=session_key, vote_type=vote_type)
        if vote_type == 'helpful':
            faq.helpful_count += 1
        else:
            faq.unhelpful_count += 1
        faq.save()

    return JsonResponse({
        'status': 'success',
        'message': 'Thank you for your feedback!',
        'helpful_count': faq.helpful_count,
        'unhelpful_count': faq.unhelpful_count,
    })
