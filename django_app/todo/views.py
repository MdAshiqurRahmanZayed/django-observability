from django.shortcuts import get_object_or_404, redirect, render

from .forms import TodoForm
from .models import Todo


def todo_list(request):
    tab = request.GET.get("tab", "pending")

    if tab == "done":
        todos = Todo.objects.filter(completed=True)
    elif tab == "pending":
        todos = Todo.objects.filter(completed=False)
    else:
        tab = "all"
        todos = Todo.objects.all()

    counts = {
        "all": Todo.objects.count(),
        "done": Todo.objects.filter(completed=True).count(),
        "pending": Todo.objects.filter(completed=False).count(),
    }

    return render(
        request,
        "todo/todo_list.html",
        {
            "todos": todos,
            "tab": tab,
            "counts": counts,
        },
    )


def todo_create(request):
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("todo:todo_list")
    else:
        form = TodoForm()
    return render(request, "todo/todo_form.html", {"form": form, "action": "Create"})


def todo_update(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if request.method == "POST":
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            return redirect("todo:todo_list")
    else:
        form = TodoForm(instance=todo)
    return render(request, "todo/todo_form.html", {"form": form, "action": "Update"})


def todo_delete(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if request.method == "POST":
        todo.delete()
        return redirect("todo:todo_list")
    return render(request, "todo/todo_confirm_delete.html", {"todo": todo})


def todo_toggle(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    todo.completed = not todo.completed
    todo.save()
    tab = request.GET.get("tab", "pending")
    return redirect(f"/?tab={tab}")
