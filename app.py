from flask import Flask, jsonify, render_template, request
import psutil

app = Flask(__name__)

# Route for the main HTML page
@app.route('/')
def home():
    return render_template('index.html')

# Route to get process data
@app.route('/processes')
def get_processes():
    process_list = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
        try:
            process_list.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return jsonify(process_list)

# Route to get CPU usage
@app.route('/cpu')
def get_cpu_usage():
    return jsonify({'cpu': psutil.cpu_percent(interval=0.5)})

# Route to get the top 5 processes by memory usage for the memory chart
@app.route('/memory')
def get_memory_usage():
    process_list = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            process_list.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Sort by memory usage and get top 5
    sorted_processes = sorted(process_list, key=lambda p: p['memory_percent'], reverse=True)[:5]
    return jsonify(sorted_processes)

# Route to get process status distribution for the status chart
@app.route('/status')
def get_status_distribution():
    status_count = {'running': 0, 'sleeping': 0, 'stopped': 0, 'zombie': 0}
    
    for proc in psutil.process_iter(['status']):
        try:
            status = proc.info['status']
            if status in status_count:
                status_count[status] += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    return jsonify(status_count)

# Route to kill a process by PID
@app.route('/kill/<int:pid>', methods=['POST'])
def kill_process(pid):
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        return jsonify({'success': True, 'message': f'Process {pid} terminated'})
    except psutil.NoSuchProcess:
        return jsonify({'success': False, 'message': 'Process not found'})
    except psutil.AccessDenied:
        return jsonify({'success': False, 'message': 'Permission denied'})


if __name__ == '__main__':
    print("✅ Starting Flask server on http://127.0.0.1:5000")
    app.run(debug=True)
