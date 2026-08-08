from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Review
from pgs.models import PG


@login_required(login_url='/dashboard/login/')
def add_review(request, id):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        pg = PG.objects.get(id=id)

        Review.objects.create(
            user=request.user,
            pg=pg,
            rating=rating,
            comment=comment
        )

    return redirect('/pg/search/')