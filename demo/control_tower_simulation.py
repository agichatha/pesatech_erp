#!/usr/bin/env python3
"""
Pesatech Control Tower - standalone simulation (no Frappe required).

Mirrors the module logic: strategy cascade, per-employee activities with points &
streak, blockers, manager weekly sign-off, and the leadership roll-up
(team completion + leaderboard + objective drilldown).
Run:  python3 control_tower_simulation.py
"""
RAG_GREEN, RAG_AMBER, POINTS = 80, 70, 10


def line(c="-"):
    print(c * 78)


def rag(p):
    return "Green" if p >= RAG_GREEN else "Amber" if p >= RAG_AMBER else "Red"


def main():
    print("=" * 78)
    print("PESATECH CONTROL TOWER - STRATEGY EXECUTION CASCADE (SIMULATION)")
    print("=" * 78)

    # 1. Cascade: objective -> targets -> activity template (per position)
    print("\nSTEP 1 - Cascade: Strategic Objective -> Targets -> Activities (per position)")
    print("  Objective: Market Expansion (FY2026)")
    print("    Target: +30% client base in new regions  (progress 64%)")
    print("    Template 'Relationship Manager' activities:")
    template = [
        ("5 outbound prospect touches", "Daily", "Market Expansion", "Outbound/day"),
        ("2 on-site visits or demos", "Weekly", "Market Expansion", "Demos/wk"),
        ("Retention check-in each client", "Monthly", "Customer Experience", "Retention"),
        ("Performance review vs contract", "Quarterly", "Talent Development", "Appraisal"),
    ]
    for a, c, o, k in template:
        print(f"      - [{c:<9}] {a:<34} -> {o} / {k}")
    print("  => generate_for_employee('Jane Wanjiru', 'Relationship Manager') creates 4 activities")
    line()

    # 2. Personal: complete activities -> points + streak; blockers captured
    print("STEP 2 - Jane's week: completions, points, streak, blockers")
    days = [("Mon", True), ("Tue", True), ("Wed", True), ("Thu", False), ("Fri", True)]
    points, streak, longest = 0, 0, 0
    for day, on_time in days:
        if on_time:
            points += POINTS; streak += 1; longest = max(longest, streak)
            print(f"  {day}: daily activity done on time   -> +{POINTS} pts | streak {streak}")
        else:
            streak = 0
            print(f"  {day}: missed (blocker logged: 'awaiting client callback') -> streak reset")
    print(f"  Week: {points} points | current streak {streak} | longest {longest}")
    line()

    # 3. Manager weekly sign-off
    print("STEP 3 - Weekly Review (manager sign-off)")
    planned, completed = 7, 6
    cr = round(100 * completed / planned)
    print(f"  Jane Wanjiru | week ending 20 Jun | completed {completed}/{planned} = {cr}%")
    print(f"  Blockers: 1 (client callback)  | points earned: {points}")
    print(f"  Manager (Sales Lead) sign-off: YES -> status 'Signed Off'")
    print("  (submission blocked by validation if sign-off missing)")
    line()

    # 4. Leadership roll-up A: completion by team
    print("STEP 4 - Leadership: activity completion by team")
    teams = [("Delivery", 91), ("Support", 84), ("Sales", 82), ("Marketing", 76), ("Finance & Admin", 68)]
    for t, p in teams:
        bar = "#" * (p // 5)
        print(f"  {t:<16} {p:>3}% {bar:<20} {rag(p)}")
    line()

    # 5. Leadership roll-up B: individual leaderboard
    print("STEP 5 - Leadership: individual leaderboard (by points)")
    board = [("Mary Otieno (Delivery)", 520, 14, 95),
             ("Jane Wanjiru (RM)", 480, 4, 88),
             ("Peter Kamau (Marketing)", 410, 7, 79),
             ("Asha Nur (Support)", 390, 9, 86)]
    print(f"  {'#':<3}{'Member':<28}{'Points':>8}{'Streak':>8}{'Compl.':>8}")
    for i, (n, pts, stk, comp) in enumerate(board, 1):
        print(f"  {i:<3}{n:<28}{pts:>8}{stk:>8}{comp:>7}%")
    line()

    # 6. Leadership roll-up C: objective-by-objective drilldown
    print("STEP 6 - Leadership: objective-by-objective drilldown")
    objs = [("Innovation & Product Leadership", 72), ("Market Expansion", 64),
            ("Customer Experience Excellence", 88), ("Operational Excellence & Governance", 70),
            ("Talent Development & Culture", 81)]
    for name, p in objs:
        flag = "  <-- AT RISK" if rag(p) == "Red" else ""
        print(f"  {name:<38} {p:>3}%  {rag(p)}{flag}")
    on_track = sum(1 for _, p in objs if rag(p) == "Green")
    print(f"  Objectives on track (Green): {on_track}/{len(objs)}")
    line("=")
    print("Simulation complete. Mirrors the Control Tower module logic:")
    print("  api.generate_for_employee (cascade)   EmployeeActivity.mark_done (points/streak)")
    print("  api.award / Tower Member (leaderboard) WeeklyReview.on_submit (manager sign-off)")
    print("  StrategicObjective.validate (RAG)      api.get_leadership_summary (roll-up)")


if __name__ == "__main__":
    main()
