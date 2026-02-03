import requests
from typing import Dict, List, Tuple
from platforms import Platforms

def display_platforms_menu() -> None:
    """
    Display all available platforms for checking.
    """
    print("\n[+] Available platforms:")
    for i, platform in enumerate(Platforms.keys(), 1):
        print(f"   {i:2d}. {platform}")
    print()

def get_selected_platforms() -> Dict[str, str]:
    """
    Let user select which platforms to check.
    
    Returns:
        Dictionary of selected platforms {name: url_template}
    """
    platform_list = list(Platforms.keys())
    
    print("\n[+] Select platforms to check:")
    print("   1. Check ALL platforms")
    print("   2. Select specific platforms")
    print("   3. Enter custom list (comma-separated numbers)")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            # Check all platforms
            return Platforms
            
        elif choice == '2':
            # Interactive selection
            selected = {}
            display_platforms_menu()
            print("Enter platform numbers one by one (enter 'done' when finished):")
            
            while True:
                selection = input("Platform # (or 'done'): ").strip().lower()
                
                if selection == 'done':
                    if not selected:
                        print("[!] No platforms selected. Please select at least one.")
                        continue
                    return selected
                
                if selection.isdigit():
                    idx = int(selection) - 1
                    if 0 <= idx < len(platform_list):
                        platform_name = platform_list[idx]
                        selected[platform_name] = Platforms[platform_name]
                        print(f"[+] Added: {platform_name}")
                    else:
                        print(f"[!] Invalid number. Please enter 1-{len(platform_list)}")
                else:
                    print("[!] Please enter a number or 'done'")
                    
        elif choice == '3':
            # Bulk input
            display_platforms_menu()
            print(f"Enter platform numbers separated by commas (e.g., 1,3,5,7):")
            
            while True:
                try:
                    selection = input("Platform numbers: ").strip()
                    if not selection:
                        print("[!] Please enter at least one number")
                        continue
                        
                    numbers = [int(n.strip()) for n in selection.split(',')]
                    selected = {}
                    
                    for num in numbers:
                        idx = num - 1
                        if 0 <= idx < len(platform_list):
                            platform_name = platform_list[idx]
                            selected[platform_name] = Platforms[platform_name]
                        else:
                            print(f"[!] Skipping invalid number: {num}")
                    
                    if selected:
                        print(f"[+] Selected {len(selected)} platform(s)")
                        return selected
                    else:
                        print("[!] No valid platforms selected. Try again.")
                        
                except ValueError:
                    print("[!] Invalid input. Please enter numbers separated by commas.")
        
        else:
            print("[!] Invalid choice. Please enter 1, 2, or 3.")

def check_username(username: str, platforms_to_check: Dict[str, str] = None) -> Tuple[Dict[str, str], List[str]]:
    """
    Check if a username exists on selected platforms.
    
    Args:
        username: The username to check
        platforms_to_check: Specific platforms to check (if None, checks all)
        
    Returns:
        Tuple containing (found_platforms, error_platforms)
    """
    if platforms_to_check is None:
        platforms_to_check = Platforms
    
    print(f"\n[+] Checking username: {username}")
    print(f"[+] Platforms to check: {', '.join(platforms_to_check.keys())}\n")
    
    found_platforms = {}
    error_platforms = []
    total_checked = 0
    
    for platform_name, url_template in platforms_to_check.items():
        profile_url = url_template.format(username)
        total_checked += 1
        
        try:
            response = requests.get(
                profile_url, 
                timeout=5,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            # Check if the profile exists
            if response.status_code == 200:
                # Some platforms return 200 even for non-existent profiles
                # We can add platform-specific checks if needed
                print(f"[✓ FOUND] {platform_name}: {profile_url}")
                found_platforms[platform_name] = profile_url
            else:
                print(f"[✗ NOT FOUND] {platform_name}")
                
        except requests.exceptions.Timeout:
            print(f"[⌛ TIMEOUT] {platform_name}")
            error_platforms.append(f"{platform_name} (timeout)")
        except requests.exceptions.ConnectionError:
            print(f"[🔌 CONNECTION ERROR] {platform_name}")
            error_platforms.append(f"{platform_name} (connection)")
        except requests.exceptions.RequestException as e:
            print(f"[⚠ ERROR] {platform_name}: {type(e).__name__}")
            error_platforms.append(f"{platform_name} ({type(e).__name__})")
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"[+] SUMMARY:")
    print(f"   • Total platforms checked: {total_checked}")
    print(f"   • Found on: {len(found_platforms)} platforms")
    print(f"   • Errors: {len(error_platforms)} platforms")
    
    if found_platforms:
        print(f"\n[+] Found profiles:")
        for platform, url in found_platforms.items():
            print(f"   • {platform}: {url}")
    
    if error_platforms:
        print(f"\n[!] Platforms with errors:")
        for error in error_platforms:
            print(f"   • {error}")
    
    return found_platforms, error_platforms

def save_results(username: str, found_platforms: Dict[str, str], filename: str = None) -> None:
    """
    Save results to a file.
    """
    if filename is None:
        filename = f"{username}_results.txt"
    
    with open(filename, 'w') as f:
        f.write(f"Username: {username}\n")
        f.write(f"Found on {len(found_platforms)} platforms:\n")
        f.write("="*50 + "\n")
        
        for platform, url in found_platforms.items():
            f.write(f"{platform}: {url}\n")
    
    print(f"\n[+] Results saved to: {filename}")

def main():
    print("Userrecon - Username Checker")
    print("=" * 50)
    
    while True:
        username = input("\nEnter username to check (or 'quit' to exit): ").strip()
        
        if username.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        if not username:
            print("[!] Please enter a valid username")
            continue
        
        # Let user select platforms
        selected_platforms = get_selected_platforms()
        
        # Check username on selected platforms
        found_platforms, error_platforms = check_username(username, selected_platforms)
        
        # Option to save results
        if found_platforms:
            save_choice = input("\nSave results to file? (y/n): ").strip().lower()
            if save_choice in ['y', 'yes']:
                save_results(username, found_platforms)
        
        # Option to continue with same selection
        print("\n" + "="*50)
        again = input("\nCheck another username? (y/n): ").strip().lower()
        if again not in ['y', 'yes']:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
