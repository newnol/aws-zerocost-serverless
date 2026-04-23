import json
import random
import threading
import time
import urllib.request
from datetime import datetime, timedelta

# ==========================================
# CẤU HÌNH API URL
# Thay thế chuỗi bên dưới bằng URL API Gateway của bạn (bao gồm cả /prod và /tasks)
# ==========================================
API_URL = "https://38o4vsfh4c.execute-api.ap-southeast-2.amazonaws.com/prod/tasks"

USER_ID = "traffic-gen-user"
created_task_ids = []
lock = threading.Lock()


def make_request(method, url, data=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "TrafficGeneratorScript/3.0 (Continuous)",
    }
    req = urllib.request.Request(url, headers=headers, method=method)
    if data:
        req.data = json.dumps(data).encode("utf-8")
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            if res_body:
                return json.loads(res_body)
            return {}
    except urllib.error.HTTPError as e:
        status_code = e.code
        # Chỉ in lỗi Throttled hoặc 500 để đỡ rác terminal khi chạy 1 tiếng
        if status_code == 429:
            pass  # Throttling là điều bình thường khi Burst, bỏ qua in ra để khỏi trôi terminal
        elif status_code >= 500:
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] SERVER ERROR ({status_code}) - {method}"
            )
        return None
    except Exception as e:
        return None


def create_task():
    data = {
        "title": f"Generated Task {random.randint(1000, 99999)}",
        "description": "Continuous testing task.",
        "priority": random.choice(["low", "medium", "high"]),
        "status": "pending",
        "userId": USER_ID,
    }
    res = make_request("POST", API_URL, data)
    if res and "taskId" in res:
        with lock:
            # Giữ list không quá to để tránh tràn bộ nhớ
            if len(created_task_ids) > 1000:
                created_task_ids.pop(0)
            created_task_ids.append(res["taskId"])


def get_tasks():
    url = f"{API_URL}?userId={USER_ID}"
    make_request("GET", url)


def update_task():
    with lock:
        if not created_task_ids:
            return
        task_id = random.choice(created_task_ids)
    url = f"{API_URL}/{task_id}"
    data = {"status": "done", "priority": "high"}
    make_request("PUT", url, data)


def delete_task():
    with lock:
        if not created_task_ids:
            return
        task_id = random.choice(created_task_ids)
        created_task_ids.remove(task_id)
    url = f"{API_URL}/{task_id}"
    make_request("DELETE", url)


def worker_burst(burst_size):
    """Bắn liên tục không ngừng trong 1 khoảng ngắn (Tạo Throttling)"""
    for _ in range(burst_size):
        action = random.choices(
            [create_task, get_tasks, update_task, delete_task],
            weights=[0.3, 0.5, 0.1, 0.1],
        )[0]
        action()


def worker_steady(duration_seconds):
    """Bắn đều đặn, chậm rãi (Tạo nền đồ thị ổn định)"""
    end_time = time.time() + duration_seconds
    while time.time() < end_time:
        action = random.choices(
            [create_task, get_tasks, update_task, delete_task],
            weights=[0.1, 0.8, 0.05, 0.05],  # Chủ yếu là GET
        )[0]
        action()
        # Chờ 0.5s - 1.5s giữa các request
        time.sleep(random.uniform(0.5, 1.5))


def run_continuous_traffic(hours=1.0):
    print(f"=== 🕰️ Starting CONTINUOUS Traffic Generator 🕰️ ===")
    print(f"Target API: {API_URL}")
    print(f"Planned duration: {hours} hours")
    print("Mode: Steady traffic with random bursts every few minutes.")
    print("====================================================\n")

    end_time = datetime.now() + timedelta(hours=hours)

    # Mồi data ban đầu
    for _ in range(10):
        create_task()

    burst_count = 0
    steady_cycles = 0

    try:
        while datetime.now() < end_time:
            current_time_str = datetime.now().strftime("%H:%M:%S")
            time_left = end_time - datetime.now()

            # Tính toán xác suất để Burst
            # ~20% cơ hội sẽ tạo ra một đợt Burst (tấn công) mỗi vòng lặp
            if random.random() < 0.20:
                burst_count += 1
                num_threads = random.randint(3, 8)
                req_per_thread = random.randint(20, 50)
                print(
                    f"[{current_time_str}] 🔥 TRIGGERING BURST TRAFFIC (Threads: {num_threads}, Reqs: {req_per_thread*num_threads})"
                )

                threads = []
                for _ in range(num_threads):
                    t = threading.Thread(target=worker_burst, args=(req_per_thread,))
                    threads.append(t)
                    t.start()
                for t in threads:
                    t.join()
                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] 📉 Burst complete. Cooling down..."
                )
                time.sleep(5)  # Nghỉ 5s sau khi burst

            else:
                steady_cycles += 1
                steady_duration = random.randint(30, 90)  # Chạy nền 30s đến 90s
                print(
                    f"[{current_time_str}] 🚶 Running steady traffic for {steady_duration} seconds... (Time left: {str(time_left).split('.')[0]})"
                )
                worker_steady(steady_duration)

    except KeyboardInterrupt:
        print("\n\n⚠️ Script stopped manually by user.")

    print("\n=== 🏁 Continuous Traffic Generation Finished 🏁 ===")
    print(f"Total Steady Cycles: {steady_cycles}")
    print(f"Total Burst Events: {burst_count}")
    print("CloudWatch will look amazing now!")


if __name__ == "__main__":
    if "YOUR_API_GATEWAY_URL_HERE" in API_URL:
        print("❌ LỖI: Bạn chưa cấu hình biến API_URL!")
    else:
        # Chạy trong 1.0 giờ (60 phút)
        run_continuous_traffic(hours=1.0)
