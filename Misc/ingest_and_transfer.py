from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import paramiko
import os
import time
import subprocess

class SegmentHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.ts'):
            print(f"New HLS segment created: {event.src_path}")
            self.transfer_file(event.src_path)

    def transfer_file(self, file_path):
        last_size = -1
        current_size = os.path.getsize(file_path)
        while current_size != last_size:
            last_size = current_size
            time.sleep(5)
            current_size = os.path.getsize(file_path)
        print(f"File {file_path} is ready for transfer.")

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            ssh_key_filepath = '/home/casey/.ssh/id_rsa'
            ssh_key = paramiko.RSAKey.from_private_key_file(ssh_key_filepath)
            ssh.connect('ec2-18-116-218-203.us-east-2.compute.amazonaws.com', username='ubuntu', pkey=ssh_key)

            scp = paramiko.SFTPClient.from_transport(ssh.get_transport())
            target_path = '/home/ubuntu/LiveTranslate/incoming_from_pi/' + os.path.basename(file_path)
            scp.put(file_path, target_path)
            scp.close()
            ssh.close()
            print(f"Transferred {file_path} to {target_path}")
        except Exception as e:
            print(f"Error occurred: {e}")

def start_ffmpeg():
    cmd = 'ffmpeg -y -f x11grab -s 1280x720 -thread_queue_size 256 -i :0.0 -r 30 -f pulse -thread_queue_size 256 -i default -c:v libx264 -c:a aac -preset veryfast -f segment -segment_time 30 -segment_format ts -g 30 -force_key_frames "expr:gte(t,n_forced*30)" "/home/casey/Videos/CCTV_13/output_%05d.ts"'
    subprocess.Popen(cmd, shell=True)

if __name__ == "__main__":
    start_ffmpeg()
    path = "/home/casey/Videos/CCTV_13"
    event_handler = SegmentHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print("Monitoring HLS segment directory for new files...")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()