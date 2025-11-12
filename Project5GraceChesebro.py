import openpyxl
import Project5Helpers

data = Project5Helpers.get_job_data()
for job in data:
    print(job)
from typing import List, Dict
import sys
import math
8
RESET = "\033[0m"
BOLD = "\033[1m"
FG_GREEN = "\033[32m"
FG_YELLOW = "\033[33m"
FG_BLUE = "\033[34m"
FG_MAGENTA = "\033[35m"
BG_RED = "\033[41m"

# Convenience wrappers
def bold(text: str) -> str:
    return f"{BOLD}{text}{RESET}"

def green(text: str) -> str:
    return f"{FG_GREEN}{text}{RESET}"

def yellow(text: str) -> str:
    return f"{FG_YELLOW}{text}{RESET}"

def blue(text: str) -> str:
    return f"{FG_BLUE}{text}{RESET}"

def magenta(text: str) -> str:
    return f"{FG_MAGENTA}{text}{RESET}"

def red_bg(text: str) -> str:
    return f"{BG_RED}{text}{RESET}"

# Format helpers

def fmt_money(value) -> str:
    """Formats a number like 123456 -> $123,456"""
    try:
        # Ensure it is numeric first
        v = float(value)
    except (TypeError, ValueError):
        return str(value)
    # Use no decimals since BLS values are annual salaries
    return f"${v:,.0f}"

# Mapping between BLS job_class and friendly menu text
JOBCLASS_TO_MENU = {
    "Information Security Analysts": "Software Security (Cyber Security)",
    "Computer Network Support Specialists": "Penetration Tester (Cyber Security)",
    "Computer Network Architects": "Mid and late career Penetration Tester (Cyber Security)",
    "Computer Occupations, All Other": "Digital Forensics  (Cyber Security)",
    "Software Developers": "Software Developer (Computer Science)",
    "Software Quality Assurance Analysts and Testers": "Software Testing SDET (Computer Science)",
    "Database Administrators": "Database Professional (Mostly Computer Science and Some Cyber Security)",
    "Web Developers": "Web Developer (Computer Science)",
    "Computer Systems Analysts": "DevOps/Those who can talk with humans and understand code and infrastructure deeply (Comp and Cybf)",
}

# Build reverse mapping: menu label -> list of job_class strings
MENU_TO_JOBCLASSES: Dict[str, List[str]] = {}
for jc, label in JOBCLASS_TO_MENU.items():
    MENU_TO_JOBCLASSES.setdefault(label, []).append(jc)

# Data access helpers

def load_data() -> List[Dict]:
    """Load list[dict] of job data from helpers.
    Each dict has keys like: state, code, job_class, ma_emp_num,
    ave_annual_salary, median_annual_salary, starting_salary, top_salary,
    and sometimes needed_skills (list of {category, skill}).
    """
    return Project5Helpers.get_job_data()

def get_rows_for_job_class(data: List[Dict], job_class: str) -> List[Dict]:
    return [row for row in data if row.get("job_class") == job_class]

def get_one_row_for_job_class(data: List[Dict], job_class: str) -> Dict:
    rows = get_rows_for_job_class(data, job_class)
    # Expecting exactly one, but be graceful
    return rows[0] if rows else {}

def prompt_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip().replace(",", "")
        try:
            # allow things like 85k or 85000
            if raw.lower().endswith("k"):
                val = float(raw[:-1]) * 1000
            else:
                val = float(raw)
            return int(val)
        except ValueError:
            print("Please enter a whole number (e.g., 85000 or 85k).")

def show_jobs_meeting_start(data: List[Dict], desired_salary: int) -> None:
    print("\nJobs with starting salary ≥ your target:")
    count = 0
    for row in data:
        try:
            start = float(row.get("starting_salary", 0) or 0)
        except (TypeError, ValueError):
            continue
        if start >= desired_salary:
            print(f"  - {row.get('job_class')}: {fmt_money(start)}")
            count += 1
    if count == 0:
        print("  (None meet your starting salary target.)")

def choose_menu_label() -> str:
    labels = list(MENU_TO_JOBCLASSES.keys())
    print("\nChoose a job area:")
    for i, label in enumerate(labels, start=1):
        print(f"  {i}. {label}")
    while True:
        choice = input("Enter number: ").strip()
        if not choice.isdigit():
            print("Please enter a valid number from the menu.")
            continue
        idx = int(choice)
        if 1 <= idx <= len(labels):
            return labels[idx - 1]
        print("Out of range. Try again.")

def choose_job_class_for_label(label: str) -> str:
    # Some labels have multiple underlying job classes
    job_classes = MENU_TO_JOBCLASSES.get(label, [])
    if not job_classes:
        return ""
    if len(job_classes) == 1:
        return job_classes[0]

    print(f"\n'{label}' maps to multiple BLS job classes. Choose one:")
    for i, jc in enumerate(job_classes, start=1):
        print(f"  {i}. {jc}")
    while True:
        raw = input("Enter number: ").strip()
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(job_classes):
                return job_classes[idx - 1]
        print("Please enter a valid number.")

# Salary comparison logic and output
def compare_and_report(row: Dict, desired_salary: int) -> None:
    job_class = row.get("job_class", "(unknown)")
    start = float(row.get("starting_salary", 0) or 0)
    median = float(row.get("median_annual_salary", 0) or 0)
    ave = float(row.get("ave_annual_salary", 0) or 0)
    top = float(row.get("top_salary", 0) or 0)
    ma_emp = row.get("ma_emp_num", 0)

    print("\nSelected job:", bold(job_class))
    print("Desired salary:", fmt_money(desired_salary))

    # Starting salary vs desired
    if start >= desired_salary:
        print(f"Starting salary meets your target: {bold(green(fmt_money(start)))}")
    else:
        print(
            f"Starting salary is below your target: "
            f"{red_bg(bold(fmt_money(start)))}"
        )
        # If starting is below desired, check median
        if median >= desired_salary:
            print(
                f"Median salary clears your target: "
                f"{bold(green(fmt_money(median)))}"
            )
        else:
            print(f"Median salary is {fmt_money(median)} (also below your target).")

    # Jobs count in MA
    print(f"Jobs in MA for this field: {bold(str(ma_emp))}")

    # Average vs median comparisons
    # If average more than 5% higher than median
    if ave >= 1.05 * median and median > 0:
        diff = ave - median
        print(
            blue(
                bold(
                    f"Average is {fmt_money(diff)} higher than median (>5%). "
                    f"A few highly paid individuals may be skewing the average."
                )
            )
        )
    elif median > ave:
        print(yellow("Median is higher than average (some low salaries may be pulling the average down)."))
    else:
        # average higher, but not by >5%
        if ave > median:
            print(magenta("Average is higher than median, but not by more than 5%."))
        else:
            # equal (rare)
            print("Average and median are approximately equal.")

    # Top salary vs desired
    if top > desired_salary:
        print(red_bg(bold(f"Top salary {fmt_money(top)} exceeds your target.")))
# Skills paging (30 at a time)

def page_skills(skills: List[Dict]) -> None:
    if not skills:
        print("\n(No skills data available for this job.)")
        return

    input("\nStop here. Press Enter/Return to see skills needed for this job...")

    page_size = 30
    total = len(skills)
    start_index = 0

    while start_index < total:
        end_index = min(start_index + page_size, total)
        print(f"\nSkills {start_index + 1}-{end_index} of {total}:")
        for i in range(start_index, end_index):
            s = skills[i]
            # Each skill dict: {"category": ..., "skill": ...}
            line = f"  - {s.get('category', '')}: {s.get('skill', '')}"
            print(line)
        start_index = end_index
        if start_index < total:
            input("\nPress Enter/Return to continue...")
        else:
            print("\nNo more skills. (End)")
# Main program
def main():
    data = load_data()

    # 1) Ask user’s desired salary
    desired = prompt_int("Enter your desired salary (e.g., 85000 or 85k): ")

    # 2) Show all jobs whose *starting salary* meets/exceeds desired
    show_jobs_meeting_start(data, desired)

    # 3) Let the user choose a friendly menu option
    label = choose_menu_label()

    # 4) If the label maps to multiple job classes, let the user pick the exact one
    job_class = choose_job_class_for_label(label)
    if not job_class:
        print("Could not resolve job class for your selection. Exiting.")
        sys.exit(0)

    # 5) Find that job’s row
    row = get_one_row_for_job_class(data, job_class)
    if not row:
        print("No data found for:", job_class)
        sys.exit(0)

    # 6) Compare salaries and report with colors per spec
    compare_and_report(row, desired)

    # 7) Pause, then show skills 30 at a time
    skills = row.get("needed_skills", [])
    page_skills(skills)

if __name__ == "__main__":
    main()
