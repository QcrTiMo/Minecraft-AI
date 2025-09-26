import torch

is_available = torch.cuda.is_available()
print(f"CUDA is available: {is_available}")

if is_available:
    device_count = torch.cuda.device_count()
    print(f"Found {device_count} CUDA device(s).")
    current_device = torch.cuda.current_device()
    print(f"Current device index: {current_device}")
    device_name = torch.cuda.get_device_name(current_device)
    print(f"Current device name: {device_name}")
else:
    print("PyTorch could not find a CUDA-enabled GPU.")
    print("Please check your NVIDIA drivers and PyTorch installation.")