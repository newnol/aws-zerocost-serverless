const API_URL =
  "https://38o4vsfh4c.execute-api.ap-southeast-2.amazonaws.com/prod"; // e.g., https://xyz.execute-api.region.amazonaws.com/prod

// Initialize
document.addEventListener("DOMContentLoaded", fetchTasks);

// Fetch all tasks
async function fetchTasks() {
  try {
    const response = await fetch(`${API_URL}/tasks`);
    if (!response.ok) throw new Error("Network response was not ok");
    const tasks = await response.json();
    renderTasks(tasks);
  } catch (error) {
    console.error("Error fetching tasks:", error);
    document.getElementById("tasks-container").innerHTML =
      '<div class="bg-red-50 text-red-600 p-4 rounded-lg shadow"><p>Error loading tasks. Make sure API_URL is set.</p></div>';
  }
}

// Render tasks to the DOM
function renderTasks(tasks) {
  const container = document.getElementById("tasks-container");
  container.innerHTML = "";

  const taskCount = document.getElementById("task-count");
  if (taskCount) {
    taskCount.innerText = tasks.length;
  }

  if (tasks.length === 0) {
    container.innerHTML =
      '<div class="text-gray-500 text-center py-8"><p>No tasks found. Add one above!</p></div>';
    return;
  }

  tasks.forEach((task) => {
    const taskElement = document.createElement("div");

    // Determine priority color
    let priorityBadgeColor = "bg-gray-100 text-gray-800";
    if (task.priority === "high")
      priorityBadgeColor = "bg-red-100 text-red-800";
    if (task.priority === "medium")
      priorityBadgeColor = "bg-yellow-100 text-yellow-800";
    if (task.priority === "low")
      priorityBadgeColor = "bg-green-100 text-green-800";

    // Determine status styling
    const isDone = task.status === "done";
    const titleClass = isDone ? "text-gray-500 line-through" : "text-gray-800";

    taskElement.className = `bg-white border rounded-xl shadow-sm p-5 mb-4 transition duration-200 hover:shadow-md ${isDone ? "opacity-75" : ""}`;
    taskElement.innerHTML = `
            <div class="flex justify-between items-start mb-3">
                <h3 class="text-lg font-semibold ${titleClass}">${escapeHtml(task.title)}</h3>
                <span class="inline-block px-2.5 py-1 rounded-full text-xs font-medium ${priorityBadgeColor}">
                    ${escapeHtml(task.priority).charAt(0).toUpperCase() + escapeHtml(task.priority).slice(1)}
                </span>
            </div>

            ${task.description ? `<p class="text-gray-600 mb-4 text-sm">${escapeHtml(task.description)}</p>` : ""}

            <div class="flex items-center text-xs text-gray-500 mb-4 space-x-4">
                ${
                  task.dueDate
                    ? `
                <div class="flex items-center">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                    <span>${escapeHtml(task.dueDate)}</span>
                </div>`
                    : ""
                }

                <div class="flex items-center">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    <span>${escapeHtml(task.status).charAt(0).toUpperCase() + escapeHtml(task.status).slice(1)}</span>
                </div>
            </div>

            <div class="flex space-x-2 pt-3 border-t border-gray-100">
                <button onclick='editTask(${JSON.stringify(task).replace(/'/g, "&#39;")})' class="flex-1 bg-white hover:bg-gray-50 text-indigo-600 font-medium py-2 px-4 border border-indigo-200 rounded-lg shadow-sm text-sm transition duration-150">
                    Edit
                </button>
                <button onclick="deleteTask('${task.taskId}')" class="flex-1 bg-white hover:bg-red-50 text-red-600 font-medium py-2 px-4 border border-red-200 rounded-lg shadow-sm text-sm transition duration-150">
                    Delete
                </button>
            </div>
        `;
    container.appendChild(taskElement);
  });
}

// Save or update a task
async function saveTask() {
  const taskId = document.getElementById("taskId").value;
  const submitBtn = document.getElementById("submit-btn");
  const originalBtnText = submitBtn.innerText;

  const taskData = {
    title: document.getElementById("title").value,
    description: document.getElementById("description").value,
    priority: document.getElementById("priority").value,
    dueDate: document.getElementById("dueDate").value,
    status: document.getElementById("status").value,
    userId: "user123", // Hardcoded user for simplicity, usually comes from auth
  };

  if (!taskData.title) {
    alert("Title is required");
    return;
  }

  // Update button state
  submitBtn.innerText = "Saving...";
  submitBtn.disabled = true;

  const method = taskId ? "PUT" : "POST";
  const url = taskId ? `${API_URL}/tasks/${taskId}` : `${API_URL}/tasks`;

  try {
    const response = await fetch(url, {
      method: method,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(taskData),
    });

    if (!response.ok) throw new Error("Network response was not ok");

    clearForm();
    await fetchTasks();
  } catch (error) {
    console.error("Error saving task:", error);
    alert("Error saving task");
  } finally {
    submitBtn.innerText = originalBtnText;
    submitBtn.disabled = false;
  }
}

// Populate form for editing
function editTask(task) {
  document.getElementById("taskId").value = task.taskId;
  document.getElementById("title").value = task.title;
  document.getElementById("description").value = task.description || "";
  document.getElementById("priority").value = task.priority || "medium";
  document.getElementById("dueDate").value = task.dueDate || "";
  document.getElementById("status").value = task.status || "pending";

  document.getElementById("submit-btn").innerText = "Update Task";

  // Scroll to top
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// Delete a task
async function deleteTask(taskId) {
  if (!confirm("Are you sure you want to delete this task?")) return;

  try {
    const response = await fetch(`${API_URL}/tasks/${taskId}`, {
      method: "DELETE",
    });

    if (!response.ok) throw new Error("Network response was not ok");

    await fetchTasks();
  } catch (error) {
    console.error("Error deleting task:", error);
    alert("Error deleting task");
  }
}

// Clear form inputs
function clearForm() {
  document.getElementById("taskId").value = "";
  document.getElementById("title").value = "";
  document.getElementById("description").value = "";
  document.getElementById("priority").value = "medium";
  document.getElementById("dueDate").value = "";
  document.getElementById("status").value = "pending";

  document.getElementById("submit-btn").innerText = "Save Task";
}

// Utility to escape HTML to prevent XSS
function escapeHtml(unsafe) {
  if (!unsafe) return "";
  return String(unsafe)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
