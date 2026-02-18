"""
Hydra-Cool: Master Execution Script
===================================
Runs every simulation scenario in the project and aggregates the output.

Usage:
    python3 run_all.py

Author: Obada Dallo
"""

import os
import subprocess
import time

def run_all_scenarios():
    root_dir = "scenarios"
    log_file = "simulation_results.log"
    
    print(f"[*] Starting Hydra-Cool Complete Simulation Suite...")
    print(f"[*] Scanning {root_dir} for scripts...")
    
    scripts = []
    for dp, dn, filenames in os.walk(root_dir):
        for f in filenames:
            if f.endswith('.py') and f != '__init__.py':
                scripts.append(os.path.join(dp, f))
    
    # Sort scripts to run in order (A -> B -> C...)
    scripts.sort()
    
    with open(log_file, "w") as log:
        log.write("Hydra-Cool Simulation Report\n")
        log.write("============================\n")
        log.write(f"Date: {time.ctime()}\n\n")
        
        for script in scripts:
            script_name = os.path.basename(script)
            header = f"\n{'='*50}\nRUNNING SCENARIO: {script_name}\n{'='*50}\n"
            print(f"--> Running {script_name}...")
            
            log.write(header)
            log.flush()
            
            start_time = time.time()
            try:
                # Capture stdout and stderr
                result = subprocess.run(['python3', script], capture_output=True, text=True)
                
                log.write(result.stdout)
                if result.stderr:
                    log.write("\n[STDERR]\n")
                    log.write(result.stderr)
                
                status = "SUCCESS" if result.returncode == 0 else "FAILED"
                elapsed = time.time() - start_time
                
                log.write(f"\n[Status: {status}] [Time: {elapsed:.2f}s]\n")
                
            except Exception as e:
                log.write(f"\n[CRITICAL ERROR] Failed to execute script: {e}\n")
    
    print(f"\n[+] All simulations complete.")
    print(f"[+] Detailed results saved to: {log_file}")

if __name__ == "__main__":
    run_all_scenarios()
