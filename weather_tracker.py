import os
import sys
import json
import time
import shutil
from datetime import datetime, timedelta
from pathlib import Path

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ORANGE = "\033[38;5;208m"
    PURPLE = "\033[38;5;141m"
    CYAN = "\033[38;5;81m"
    GREEN = "\033[38;5;114m"
    RED = "\033[38;5;204m"
    YELLOW = "\033[38;5;221m"
    GRAY = "\033[38;5;245m"
    WHITE = "\033[38;5;255m"
    
    BG_DARK = "\033[48;5;236m"
    BG_DARKER = "\033[48;5;234m"

DATA_FILE = Path(__file__).parent / "weather_data.txt"

def get_terminal_size():
    """Get current terminal dimensions"""
    size = shutil.get_terminal_size((80, 24))
    return size.columns, size.lines

def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')

def move_cursor(x, y):
    """Move cursor to position"""
    print(f"\033[{y};{x}H", end="")

def hide_cursor():
    print("\033[?25l", end="")

def show_cursor():
    print("\033[?25h", end="")

def center_text(text, width):
    """Center text within given width"""
    text_len = len(text.replace('\033[', '').split('m')[-1]) if '\033[' in text else len(text)
    import re
    clean = re.sub(r'\033\[[0-9;]*m', '', text)
    padding = (width - len(clean)) // 2
    return " " * max(0, padding) + text

def draw_box(x, y, width, height, title=""):
    """Draw a box at position"""
    c = Colors
    
    move_cursor(x, y)
    print(f"{c.GRAY}╭{'─' * (width - 2)}╮{c.RESET}", end="")
    
    if title:
        move_cursor(x + 2, y)
        print(f"{c.GRAY}┤ {c.ORANGE}{c.BOLD}{title}{c.RESET}{c.GRAY} ├{c.RESET}", end="")
    
    for i in range(1, height - 1):
        move_cursor(x, y + i)
        print(f"{c.GRAY}│{' ' * (width - 2)}│{c.RESET}", end="")
    
    move_cursor(x, y + height - 1)
    print(f"{c.GRAY}╰{'─' * (width - 2)}╯{c.RESET}", end="")

def animate_value(start, end, x, y, duration=0.5, prefix="", suffix="", color=""):
    """Animate a number changing"""
    steps = 20
    delay = duration / steps
    
    for i in range(steps + 1):
        current = start + (end - start) * (i / steps)
        move_cursor(x, y)
        print(f"{color}{prefix}{current:.1f}{suffix}{Colors.RESET}    ", end="")
        sys.stdout.flush()
        time.sleep(delay)

def load_data():
    """Load weather data from file"""
    data = []
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and ',' in line:
                        parts = line.split(',')
                        if len(parts) >= 2:
                            date_str = parts[0].strip()
                            temp = float(parts[1].strip())
                            data.append({'date': date_str, 'temp': temp})
        except Exception as e:
            pass
    return data

def save_data(data):
    """Save weather data to file"""
    with open(DATA_FILE, 'w') as f:
        for entry in data:
            f.write(f"{entry['date']},{entry['temp']}\n")

def calculate_stats(data):
    """Calculate temperature statistics"""
    if not data:
        return None, None, None
    
    temps = [d['temp'] for d in data]
    return max(temps), min(temps), sum(temps) / len(temps)

def draw_header(width):
    """Draw the application header"""
    c = Colors
    move_cursor(1, 1)
    
    header = f"{c.ORANGE}{c.BOLD}☀  WEATHER TRACKER{c.RESET}"
    print(center_text(header, width))
    
    move_cursor(1, 2)
    subtitle = f"{c.GRAY}━{'━' * (width - 2)}━{c.RESET}"
    print(subtitle)

def draw_stats_panel(data, start_y, width):
    """Draw the statistics panel"""
    c = Colors
    high, low, avg = calculate_stats(data)
    
    panel_width = min(60, width - 4)
    panel_x = (width - panel_width) // 2
    
    draw_box(panel_x, start_y, panel_width, 8, "Temperature Stats")
    
    if data:
        move_cursor(panel_x + 4, start_y + 2)
        print(f"{c.WHITE}Highest:{c.RESET}  {c.RED}{c.BOLD}{high:>6.1f}°{c.RESET}", end="")
        
        move_cursor(panel_x + 4, start_y + 3)
        print(f"{c.WHITE}Lowest:{c.RESET}   {c.CYAN}{c.BOLD}{low:>6.1f}°{c.RESET}", end="")
        
        move_cursor(panel_x + 4, start_y + 4)
        print(f"{c.WHITE}Average:{c.RESET}  {c.YELLOW}{c.BOLD}{avg:>6.1f}°{c.RESET}", end="")
        
        move_cursor(panel_x + 4, start_y + 6)
        print(f"{c.GRAY}Total entries: {len(data)}{c.RESET}", end="")
        
        if high != low:
            bar_width = panel_width - 30
            move_cursor(panel_x + 22, start_y + 2)
            print(f"{c.RED}{'█' * bar_width}{c.RESET}", end="")
            
            move_cursor(panel_x + 22, start_y + 3)
            print(f"{c.CYAN}{'█' * int(bar_width * (low - low) / (high - low + 0.1) + 1)}{c.RESET}", end="")
            
            move_cursor(panel_x + 22, start_y + 4)
            avg_bar = int(bar_width * (avg - low) / (high - low + 0.1))
            print(f"{c.YELLOW}{'█' * max(1, avg_bar)}{c.RESET}", end="")
    else:
        move_cursor(panel_x + 4, start_y + 3)
        print(f"{c.DIM}No data available. Add your first entry!{c.RESET}", end="")
    
    return start_y + 9

def draw_recent_entries(data, start_y, width, max_entries=5):
    """Draw recent entries panel"""
    c = Colors
    
    panel_width = min(60, width - 4)
    panel_x = (width - panel_width) // 2
    panel_height = min(max_entries + 4, 10)
    
    draw_box(panel_x, start_y, panel_width, panel_height, "Recent Entries")
    
    if data:
        recent = sorted(data, key=lambda x: x['date'], reverse=True)[:max_entries]
        for i, entry in enumerate(recent):
            move_cursor(panel_x + 4, start_y + 2 + i)
            temp = entry['temp']
            temp_color = c.RED if temp > 25 else c.CYAN if temp < 10 else c.GREEN
            print(f"{c.GRAY}{entry['date']}{c.RESET}  {temp_color}{temp:>6.1f}°{c.RESET}", end="")
    else:
        move_cursor(panel_x + 4, start_y + 2)
        print(f"{c.DIM}No entries yet{c.RESET}", end="")
    
    return start_y + panel_height + 1

def draw_menu(start_y, width):
    """Draw the menu options"""
    c = Colors
    
    panel_width = min(60, width - 4)
    panel_x = (width - panel_width) // 2
    
    move_cursor(panel_x, start_y)
    print(f"{c.GRAY}─{'─' * (panel_width - 2)}─{c.RESET}")
    
    move_cursor(panel_x, start_y + 2)
    print(f"  {c.ORANGE}[A]{c.RESET} {c.WHITE}Add new entry{c.RESET}", end="")
    
    move_cursor(panel_x, start_y + 3)
    print(f"  {c.ORANGE}[V]{c.RESET} {c.WHITE}View all entries{c.RESET}", end="")
    
    move_cursor(panel_x, start_y + 4)
    print(f"  {c.ORANGE}[D]{c.RESET} {c.WHITE}Delete entry{c.RESET}", end="")
    
    move_cursor(panel_x, start_y + 5)
    print(f"  {c.ORANGE}[Q]{c.RESET} {c.WHITE}Quit{c.RESET}", end="")
    
    return start_y + 7

def date_picker(start_y, width):
    """Interactive date picker"""
    c = Colors
    show_cursor()
    
    panel_width = min(60, width - 4)
    panel_x = (width - panel_width) // 2
    
    current_date = datetime.now()
    
    clear_screen()
    draw_header(width)
    
    draw_box(panel_x, 4, panel_width, 12, "Select Date")
    
    # Instructions
    move_cursor(panel_x + 4, 6)
    print(f"{c.GRAY}Use arrow keys or enter date manually{c.RESET}", end="")
    
    move_cursor(panel_x + 4, 8)
    print(f"{c.WHITE}Format: YYYY-MM-DD{c.RESET}", end="")
    
    move_cursor(panel_x + 4, 10)
    print(f"{c.CYAN}Today: {current_date.strftime('%Y-%m-%d')}{c.RESET}", end="")
    
    move_cursor(panel_x + 4, 12)
    print(f"{c.ORANGE}Enter date (or press Enter for today): {c.RESET}", end="")
    
    sys.stdout.flush()
    
    date_input = input().strip()
    
    if not date_input:
        return current_date.strftime('%Y-%m-%d')
    
    # Validate date
    try:
        datetime.strptime(date_input, '%Y-%m-%d')
        return date_input
    except ValueError:
        move_cursor(panel_x + 4, 14)
        print(f"{c.RED}Invalid date format! Using today's date.{c.RESET}", end="")
        sys.stdout.flush()
        time.sleep(1.5)
        return current_date.strftime('%Y-%m-%d')

def add_entry(data, width, height):
    """Add a new temperature entry"""
    c = Colors
    
    # Get date
    date_str = date_picker(4, width)
    
    clear_screen()
    draw_header(width)
    
    panel_width = min(60, width - 4)
    panel_x = (width - panel_width) // 2
    
    draw_box(panel_x, 4, panel_width, 8, "Add Temperature")
    
    move_cursor(panel_x + 4, 6)
    print(f"{c.WHITE}Date: {c.CYAN}{date_str}{c.RESET}", end="")
    
    move_cursor(panel_x + 4, 8)
    print(f"{c.ORANGE}Enter temperature (°C): {c.RESET}", end="")
    
    show_cursor()
    sys.stdout.flush()
    
    try:
        temp_input = input().strip()
        temp = float(temp_input)
        
        # Check if date already exists
        existing = next((i for i, d in enumerate(data) if d['date'] == date_str), None)
        
        old_avg = calculate_stats(data)[2] if data else temp
        
        if existing is not None:
            data[existing]['temp'] = temp
            move_cursor(panel_x + 4, 10)
            print(f"{c.YELLOW}Updated existing entry{c.RESET}", end="")
        else:
            data.append({'date': date_str, 'temp': temp})
            move_cursor(panel_x + 4, 10)
            print(f"{c.GREEN}Entry added!{c.RESET}", end="")
        
        # Save and animate
        save_data(data)
        
        new_avg = calculate_stats(data)[2]
        
        hide_cursor()
        
        # Animate the average update
        move_cursor(panel_x + 4, 11)
        print(f"{c.WHITE}Average updating...{c.RESET}", end="")
        
        if old_avg is not None and new_avg is not None:
            animate_value(old_avg, new_avg, panel_x + 4, 11, 0.8, 
                         "New Average: ", "°", c.YELLOW + c.BOLD)
        
        sys.stdout.flush()
        time.sleep(1)
        
    except ValueError:
        move_cursor(panel_x + 4, 10)
        print(f"{c.RED}Invalid temperature!{c.RESET}", end="")
        sys.stdout.flush()
        time.sleep(1.5)
    
    return data

def view_all_entries(data, width, height):
    """View all entries with pagination"""
    c = Colors
    hide_cursor()
    
    if not data:
        clear_screen()
        draw_header(width)
        move_cursor(4, 5)
        print(f"{c.DIM}No entries to display{c.RESET}")
        move_cursor(4, 7)
        print(f"{c.GRAY}Press any key to continue...{c.RESET}")
        sys.stdout.flush()
        input()
        return
    
    sorted_data = sorted(data, key=lambda x: x['date'], reverse=True)
    entries_per_page = height - 10
    total_pages = (len(sorted_data) + entries_per_page - 1) // entries_per_page
    current_page = 0
    
    while True:
        clear_screen()
        draw_header(width)
        
        panel_width = min(70, width - 4)
        panel_x = (width - panel_width) // 2
        
        draw_box(panel_x, 4, panel_width, entries_per_page + 4, 
                f"All Entries (Page {current_page + 1}/{total_pages})")
        
        start_idx = current_page * entries_per_page
        end_idx = min(start_idx + entries_per_page, len(sorted_data))
        
        for i, entry in enumerate(sorted_data[start_idx:end_idx]):
            move_cursor(panel_x + 4, 6 + i)
            temp = entry['temp']
            temp_color = c.RED if temp > 25 else c.CYAN if temp < 10 else c.GREEN
            print(f"{c.GRAY}{entry['date']}{c.RESET}  {temp_color}{temp:>7.1f}°{c.RESET}", end="")
        
        move_cursor(panel_x, entries_per_page + 9)
        print(f"  {c.GRAY}[N] Next  [P] Previous  [Q] Back{c.RESET}", end="")
        
        show_cursor()
        sys.stdout.flush()
        
        choice = input().strip().lower()
        
        if choice == 'n' and current_page < total_pages - 1:
            current_page += 1
        elif choice == 'p' and current_page > 0:
            current_page -= 1
        elif choice == 'q':
            break

def delete_entry(data, width, height):
    """Delete an entry"""
    c = Colors
    
    if not data:
        clear_screen()
        draw_header(width)
        move_cursor(4, 5)
        print(f"{c.DIM}No entries to delete{c.RESET}")
        time.sleep(1.5)
        return data
    
    clear_screen()
    draw_header(width)
    
    panel_width = min(60, width - 4)
    panel_x = (width - panel_width) // 2
    
    draw_box(panel_x, 4, panel_width, 6, "Delete Entry")
    
    move_cursor(panel_x + 4, 6)
    print(f"{c.ORANGE}Enter date to delete (YYYY-MM-DD): {c.RESET}", end="")
    
    show_cursor()
    sys.stdout.flush()
    
    date_input = input().strip()
    
    # Find and remove entry
    original_len = len(data)
    data = [d for d in data if d['date'] != date_input]
    
    if len(data) < original_len:
        save_data(data)
        move_cursor(panel_x + 4, 8)
        print(f"{c.GREEN}Entry deleted!{c.RESET}", end="")
    else:
        move_cursor(panel_x + 8)
        print(f"{c.RED}Entry not found{c.RESET}", end="")
    
    sys.stdout.flush()
    time.sleep(1.5)
    
    return data

def draw_loading_animation(width, height):
    """Show loading animation on startup"""
    c = Colors
    hide_cursor()
    clear_screen()
    
    center_y = height // 2
    
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    for i in range(15):
        move_cursor(1, center_y)
        frame = frames[i % len(frames)]
        text = f"{c.ORANGE}{frame} Loading Weather Tracker...{c.RESET}"
        print(center_text(text, width), end="")
        sys.stdout.flush()
        time.sleep(0.1)
    
    # Final flash
    clear_screen()
    move_cursor(1, center_y)
    print(center_text(f"{c.ORANGE}{c.BOLD}☀  WEATHER TRACKER{c.RESET}", width))
    sys.stdout.flush()
    time.sleep(0.3)

def main():
    """Main application loop"""
    c = Colors
    
    try:
        # Get terminal size
        width, height = get_terminal_size()
        
        # Show loading animation
        draw_loading_animation(width, height)
        
        # Load existing data
        data = load_data()
        
        while True:
            # Refresh terminal size each loop
            width, height = get_terminal_size()
            
            hide_cursor()
            clear_screen()
            
            # Draw UI
            draw_header(width)
            next_y = draw_stats_panel(data, 4, width)
            next_y = draw_recent_entries(data, next_y, width)
            menu_y = draw_menu(next_y, width)
            
            # Prompt
            panel_width = min(60, width - 4)
            panel_x = (width - panel_width) // 2
            
            move_cursor(panel_x, menu_y + 1)
            print(f"{c.ORANGE}❯{c.RESET} ", end="")
            
            show_cursor()
            sys.stdout.flush()
            
            choice = input().strip().lower()
            
            if choice == 'a':
                data = add_entry(data, width, height)
            elif choice == 'v':
                view_all_entries(data, width, height)
            elif choice == 'd':
                data = delete_entry(data, width, height)
            elif choice == 'q':
                clear_screen()
                move_cursor(1, 1)
                print(f"{c.ORANGE}Goodbye! ☀{c.RESET}")
                show_cursor()
                break
    
    except KeyboardInterrupt:
        clear_screen()
        move_cursor(1, 1)
        print(f"{Colors.ORANGE}Goodbye! ☀{Colors.RESET}")
        show_cursor()
    
    finally:
        show_cursor()

if __name__ == "__main__":
    main()
