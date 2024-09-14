from django.shortcuts import render,get_object_or_404,redirect
from django.utils import timezone
from .models import Post
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.utils import timezone
from django.db.models.functions import TruncDate,TruncHour
from django.db.models import Count
from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count


from .models import Post
from django.http import JsonResponse

def post_list(request):
    today = timezone.now()
    filter_type = request.GET.get('filter', 'monthly')  # Default to 'monthly'

    if filter_type == 'daily':
        today_posts = Post.objects.filter(created_date__date=today.date())
        daily_data = today_posts.annotate(date=TruncDate('created_date')).values('date').annotate(count=Count('id')).order_by('date')
        data = {'labels': [item['date'].strftime('%H:%M') for item in daily_data], 'counts': [item['count'] for item in daily_data]}

    elif filter_type == 'weekly':
        week_start = today - timedelta(days=today.weekday())  # Start of the week (Monday)
        week_end = week_start + timedelta(days=6)  # End of the week (Sunday)
        week_posts = Post.objects.filter(created_date__date__range=[week_start, week_end])
        weekly_data = week_posts.annotate(day=TruncDate('created_date')).values('day').annotate(count=Count('id')).order_by('day')
        data = {'labels': [item['day'].strftime('%A') for item in weekly_data], 'counts': [item['count'] for item in weekly_data]}

    else:  # Default to 'monthly'
        month_posts = Post.objects.filter(
            created_date__year=today.year,
            created_date__month=today.month
        )
        monthly_data = month_posts.annotate(date=TruncDate('created_date')).values('date').annotate(count=Count('id')).order_by('date')
        data = {'labels': [item['date'].strftime('%d') for item in monthly_data], 'counts': [item['count'] for item in monthly_data]}

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(data)

    return render(request, 'blog/post_list1.html', {'data': data, 'filter_type': filter_type})





# def post_list(request):
#     today = timezone.now()

#     # Filter for the current week posts
#     week_start = today - timedelta(days=today.weekday())  # Start of the week (Monday)
#     week_end = week_start + timedelta(days=6)  # End of the week (Sunday)
#     week_posts = Post.objects.filter(created_date__date__range=[week_start, week_end])

#     # Filter for the current month posts
#     month_posts = Post.objects.filter(
#         created_date__year=today.year,
#         created_date__month=today.month
#     )

#     # Aggregating posts by day of the week (for weekly graph)
#     weekly_data = week_posts.annotate(day=TruncDate('created_date')).values('day').annotate(count=Count('id')).order_by('day')

#     # Aggregating posts by date (for monthly graph)
#     monthly_data = month_posts.annotate(date=TruncDate('created_date')).values('date').annotate(count=Count('id')).order_by('date')

#     # Convert datetime objects to strings for monthly graph
#     monthly_data = [{'date': item['date'].strftime('%d-%m'), 'count': item['count']} for item in monthly_data]

#     # Convert datetime objects to strings for weekly graph
#     weekly_data = [{'day': item['day'].strftime('%A'), 'count': item['count']} for item in weekly_data]

#     context = {
#         'weekly_data': weekly_data,
#         'monthly_data': monthly_data,
#     }

#     return render(request, 'blog/post_list1.html', context)


# def post_list(request):
#     today = timezone.now()

#     # Filter for today's posts
#     today_posts = Post.objects.filter(created_date__date=today.date())

#     # Filter for the current week posts
#     week_start = today - timedelta(days=today.weekday())  # Start of the week (Monday)
#     week_end = week_start + timedelta(days=6)  # End of the week (Sunday)
#     week_posts = Post.objects.filter(created_date__date__range=[week_start, week_end])

#     # Filter for the current month posts
#     month_posts = Post.objects.filter(
#         created_date__year=today.year,
#         created_date__month=today.month
#     )

#     # Aggregating posts by hour (for daily graph)
#     hourly_data = today_posts.annotate(hour=TruncHour('created_date')).values('hour').annotate(count=Count('id')).order_by('hour')

#     # Aggregating posts by day of the week (for weekly graph)
#     weekly_data = week_posts.annotate(day=TruncDate('created_date')).values('day').annotate(count=Count('id')).order_by('day')

#     # Aggregating posts by date (for monthly graph)
#     monthly_data = month_posts.annotate(date=TruncDate('created_date')).values('date').annotate(count=Count('id')).order_by('date')

#     # Convert datetime objects to strings
#     hourly_data = [{'hour': format(item['hour'], 'H:i'), 'count': item['count']} for item in hourly_data]
#     weekly_data = [{'day': format(item['day'], 'l'), 'count': item['count']} for item in weekly_data]
#     monthly_data = [{'date': format(item['date'], 'j'), 'count': item['count']} for item in monthly_data]

#     context = {
#         'hourly_data': hourly_data,
#         'weekly_data': weekly_data,
#         'monthly_data': monthly_data,
#     }

#     return render(request, 'blog/post_list1.html', context)







    

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


@login_required(login_url='/accounts/login/')
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)    
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

