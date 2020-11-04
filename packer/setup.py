# dummy python startup script to demonstrate cloud-init
import psutil

if __name__ == "__main__":
    vcores = psutil.cpu_count(logical=True)
    pcores = psutil.cpu_count(logical=False)
    print("startup.py: Physical Cores: %d Logical Cores: %d" % (pcores,vcores))
