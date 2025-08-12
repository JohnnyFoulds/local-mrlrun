# Containerd Cleanup Guide

## Fix the file descriptor limits first

```bash
sudo sysctl -w fs.inotify.max_user_watches=524288
sudo sysctl -w fs.inotify.max_user_instances=512
```

```bash
sudo du -sh /var/lib/rancher/k3s/agent/containerd/

# First get a list of snapshot IDs
sudo ls -1 /var/lib/rancher/k3s/agent/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/ > /tmp/snapshots.txt

# Then check sizes for each
for snap in $(cat /tmp/snapshots.txt); do
  size=$(sudo du -sh /var/lib/rancher/k3s/agent/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/$snap 2>/dev/null | cut -f1)
  echo "$size $snap"
done | sort -hr | head -20

# sudo ls -la /var/lib/rancher/k3s/agent/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/
# sudo ls -la /var/lib/rancher/k3s/agent/containerd/io.containerd.content.v1.content/blobs/sudo find /var/lib/rancher/k3s/agent/containerd -type d -maxdepth 1 -exec du -sh {} \;
```

### What's happening:

When containers run, containerd creates overlay filesystem snapshots. These don't always get cleaned up properly when containers are removed, especially if they were forcibly terminated or if the system wasn't shut down gracefully.

### Safe cleanup options:

1. **Prune unused images and containers:**
```bash
sudo k3s crictl rmi --prune
```

2. **Stop and clean up stopped containers:**
```bash
sudo crictl ps -a | grep Exited | awk '{print $1}' | xargs -r sudo crictl rm
```

3. **Restart K3s** (which can trigger some cleanup):
```bash
sudo systemctl restart k3s
```

### More aggressive cleanup (if needed):

If the above doesn't free enough space, you can try a more aggressive approach:

1. **Stop K3s:**
```bash
sudo systemctl stop k3s
```

2. **Clean up the snapshots:**
```bash
sudo rm -rf /var/lib/rancher/k3s/agent/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/*
sudo rm -rf /var/lib/rancher/k3s/agent/containerd/io.containerd.content.v1.content/blobs/*
```

3. **Restart K3s:**
```bash
sudo systemctl start k3s
```

This will remove all container snapshots, which means your running containers will be removed. K3s will recreate the essential system containers upon restart, but you'll need to redeploy your own workloads.

Would you like me to provide instructions for setting up periodic cleanup to prevent this from happening again?



## Harder than it looks, try again

```bash
# Remove stopped containers only
sudo k3s crictl ps -a
sudo k3s crictl rm $(sudo k3s crictl ps -a -q | grep -vFf <(sudo k3s crictl ps -q))

# Remove exited/unused pod sandboxes
sudo k3s crictl pods -o json | jq -r '.items[] | select(.status.state != "SANDBOX_READY") | .id' | xargs -r sudo k3s crictl rmp

# Prune unused images (and associated unused snapshots)
sudo k3s crictl rmi --prune

# Verify snapshot directory size before and after:
sudo du -sh /var/lib/rancher/k3s/agent/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/

```