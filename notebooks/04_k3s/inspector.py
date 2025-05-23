import os
import json
import subprocess
import platform
import sys

def inspect_environment(context):
    """
    Collects and logs information about the Docker container's environment.
    """
    context.logger.info("Starting environment inspection...")

    # 1. Environment Variables
    env_vars = dict(os.environ)
    context.logger.info("--- Environment Variables ---")
    # Log them individually for easier reading in MLRun UI logs
    for key, value in sorted(env_vars.items()):
        context.logger.info(f"{key}={value}")
    # Also log as a JSON artifact for structured output
    #context.log_artifact("environment_variables", body=json.dumps(env_vars, indent=4), format="json")

    # 2. Mount Points / Filesystem Information
    # This is more platform-dependent and might require permissions
    context.logger.info("--- Mount Points (from /proc/mounts) ---")
    mount_info = "Could not read /proc/mounts"
    try:
        with open("/proc/mounts", "r") as f:
            mount_info = f.read()
        context.logger.info(mount_info)
        #context.log_artifact("mounts_proc", body=mount_info, format="txt")
    except Exception as e:
        context.logger.error(f"Error reading /proc/mounts: {e}")
        context.log_artifact("mounts_proc_error", body=str(e), format="txt")

    context.logger.info("--- Filesystem Root Listing (ls -la /) ---")
    try:
        root_ls = subprocess.check_output(["ls", "-la", "/"], text=True, stderr=subprocess.STDOUT)
        context.logger.info(root_ls)
        #context.log_artifact("ls_root", body=root_ls, format="txt")
    except Exception as e:
        context.logger.error(f"Error listing /: {e}")
        context.log_artifact("ls_root_error", body=str(e), format="txt")

    context.logger.info("--- Specific Directory Listings ---")
    dirs_to_check = ["/mlrun", "/data", "/v3io", "/mnt", "/etc", "/opt", os.getcwd()]
    for d in dirs_to_check:
        context.logger.info(f"--- Listing for {d} (ls -la {d}) ---")
        try:
            dir_ls = subprocess.check_output(["ls", "-la", d], text=True, stderr=subprocess.STDOUT)
            context.logger.info(dir_ls)
            #context.log_artifact(f"ls_{d.replace('/', '_')}", body=dir_ls, format="txt")
        except Exception as e:
            context.logger.warn(f"Could not list {d}: {e}")
            # context.log_artifact(f"ls_{d.replace('/', '_')}_error", body=str(e), format="txt")


    # 3. Python Interpreter and MLRun Context Info
    context.logger.info("--- Python & System Info ---")
    context.logger.info(f"Python Version: {sys.version}")
    context.logger.info(f"Platform: {platform.platform()}")
    context.logger.info(f"Current Working Directory: {os.getcwd()}")
    context.logger.info(f"Command line arguments to script (sys.argv): {sys.argv}")

    context.logger.info("--- MLRun Context Info ---")
    context_dict = context.to_dict()
    context.logger.info(json.dumps(context_dict, indent=4, default=str)) # Use default=str for non-serializable items
    #context.log_artifact("mlrun_context", body=json.dumps(context_dict, indent=4, default=str), format="json")


    # 4. User and Group ID
    context.logger.info("--- User/Group ID ---")
    try:
        uid = os.getuid()
        gid = os.getgid()
        user_info = subprocess.check_output(["id"], text=True, stderr=subprocess.STDOUT)
        context.logger.info(f"UID: {uid}, GID: {gid}")
        context.logger.info(f"id command output:\n{user_info}")
        #context.log_artifact("user_info", body=f"UID: {uid}, GID: {gid}\n\n{user_info}", format="txt")
    except Exception as e:
        context.logger.error(f"Could not get user/group info: {e}")

    context.logger.info("Environment inspection finished.")
    context.log_result("inspection_status", "completed")

if __name__ == '__main__':
    # This part is for local testing if needed, MLRun will call the handler directly
    # For MLRun, it will invoke `inspect_environment` through its mechanisms
    print("Running inspector script directly (not via MLRun handler call)")
    # Mock a context for local testing if you want, otherwise MLRun provides it
    class MockContext:
        def __init__(self):
            self.project = "local_test"
            self.name = "inspector_direct_run"
        def logger(self): return self # basic logging
        def info(self, msg): print(f"INFO: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def warn(self, msg): print(f"WARN: {msg}")
        def log_artifact(self, key, body, format): print(f"ARTIFACT: {key} ({format}) = {body[:100]}...")
        def log_result(self, key, value): print(f"RESULT: {key} = {value}")
        def to_dict(self): return {"project": self.project, "name": self.name, "mocked": True}