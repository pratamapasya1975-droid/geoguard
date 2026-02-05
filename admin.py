import sqlite3
import os

DB_NAME = "geoguard.db"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def set_location():
    print("\n--- SET ATTENDANCE ZONE ---")
    name = input("Location Name (e.g., Office HQ): ")
    lat = input("Latitude (e.g., -6.91474): ")
    lon = input("Longitude (e.g., 107.60981): ")
    radius = input("Allowed Radius (meters): ")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Clear old location for this demo
    c.execute("DELETE FROM locations") 
    c.execute("INSERT INTO locations (name, lat, lon, radius) VALUES (?, ?, ?, ?)", 
              (name, float(lat), float(lon), float(radius)))
    conn.commit()
    conn.close()
    print("✅ Location Updated Successfully.")

def view_logs():
    print("\n--- REAL-TIME ATTENDANCE LOGS ---")
    # Format tabel diperlebar untuk koordinat
    print(f"{'User':<10} | {'Time':<18} | {'Status':<8} | {'Dist':<6} | {'IP':<15} | {'Coords'}")
    print("-" * 90)
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id, timestamp, status, distance, ip_address, captured_lat, captured_lon FROM attendance ORDER BY id DESC LIMIT 15")
    rows = c.fetchall()
    
    for row in rows:
        coords = f"{row[5]:.4f},{row[6]:.4f}"
        print(f"{row[0]:<10} | {row[1][5:]:<18} | {row[2]:<8} | {int(row[3])}m | {row[4]:<15} | {coords}")
    conn.close()
    input("\n[Enter] Kembali...")

def main():
    while True:
        clear_screen()
        print("██████╗ ███████╗ ██████╗")
        print("██╔════╝ ██╔════╝██╔═══██╗")
        print("██║  ███╗█████╗  ██║   ██║GUARD ADMIN CLI")
        print("██║   ██║██╔══╝  ██║   ██║----------------")
        print("╚██████╔╝███████╗╚██████╔╝ [Server Only]")
        print(" ╚═════╝ ╚══════╝ ╚═════╝ ")
        print("\n1. Set Target Location")
        print("2. View Live Logs")
        print("3. Exit")
        
        choice = input("\nSelect Option: ")
        
        if choice == '1':
            set_location()
        elif choice == '2':
            view_logs()
        elif choice == '3':
            break

if __name__ == "__main__":
    main()

    