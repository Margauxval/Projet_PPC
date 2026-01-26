import pygame
import time
from pygame.locals import *

def draw_graph(screen, history):
    if not history: return
    margin, width, height, base_y = 60, 680, 180, 540
    max_val = max([max(h[0], h[1], h[2]//10, 1) for h in history])
    for i in range(len(history) - 1):
        x1 = margin + (i * width // len(history))
        x2 = margin + ((i + 1) * width // len(history))
        data = [(history[i][0], history[i+1][0], (255, 255, 255)), 
                (history[i][1], history[i+1][1], (255, 100, 100)), 
                (history[i][2]//10, history[i+1][2]//10, (100, 255, 100))]
        for v1, v2, color in data:
            y1 = base_y - (v1 * height // max_val)
            y2 = base_y - (v2 * height // max_val)
            pygame.draw.line(screen, color, (x1, y1), (x2, y2), 2)

def show_bilan(screen, font_l, font_s, texte_bilan, history):
    running = True
    while running:
        screen.fill((20, 30, 20))
        screen.blit(font_l.render("BILAN ANALYTIQUE FINAL", True, (255, 255, 255)), (200, 30))
        y_offset = 80
        for line in texte_bilan.split(" | "):
            screen.blit(font_s.render(line, True, (200, 255, 200)), (60, y_offset))
            y_offset += 25
        draw_graph(screen, history)
        screen.blit(font_s.render("Graphique : Blanc=Proies, Rouge=Preds, Vert=Herbe/10", True, (150, 150, 150)), (60, 340))
        screen.blit(font_l.render("Appuyez sur n'importe quelle touche pour quitter", True, (255, 255, 0)), (100, 560))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type in (QUIT, KEYDOWN): running = False

def display_process(shared_state, msg_queue, lock):
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("EcoSim - Dashboard Expert")
    font_l, font_m, font_s = pygame.font.Font(None, 38), pygame.font.Font(None, 28), pygame.font.Font(None, 22)
    clock = pygame.time.Clock()

    history = []
    stats = {"naiss_p": 0, "naiss_d": 0, "morts_p": 0, "morts_d": 0}
    last_hist = time.time()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT: msg_queue.put(("CMD", "STOP"))
            if event.type == KEYDOWN:
                if event.key == K_q: msg_queue.put(("CMD", "STOP"))
                if event.key == K_d: msg_queue.put(("CMD", "FORCED_DROUGHT"))

        while not msg_queue.empty():
            try:
                msg = msg_queue.get_nowait()
                if isinstance(msg, tuple) and msg[0] == "BILAN":
                    show_bilan(screen, font_l, font_s, msg[1], history); return
                if "Naissance proie" in msg: stats["naiss_p"] += 1
                elif "Naissance prédateur" in msg: stats["naiss_d"] += 1
                elif "morte" in msg or "PRÉDATION" in msg: stats["morts_p"] += 1
                elif "mort" in msg: stats["morts_d"] += 1
            except: break

        if time.time() - last_hist > 0.5:
            with lock: history.append((shared_state["num_preys"], shared_state["num_predators"], shared_state["grass"]))
            last_hist = time.time()

        screen.fill((10, 10, 15))
        with lock:
            cp, cd, cg = shared_state["num_preys"], shared_state["num_predators"], shared_state["grass"]
            ca_p = shared_state["num_active_preys"]
            # Si vous n'avez pas encore num_active_preds dans shared_state, on l'estime pour l'affichage
            ca_d = shared_state.get("num_active_predators", cd // 2) 
            drought_on = shared_state.get("drought_active", False)
        
        # --- BLOC 1 : POPULATIONS ET ALERTE ---
        bg_pop = (70, 20, 20) if drought_on else (30, 30, 50)
        pygame.draw.rect(screen, bg_pop, (30, 20, 740, 90), border_radius=8)
        txt_title = "!!! SÉCHERESSE EN COURS !!!" if drought_on else "1. POPULATIONS ACTUELLES"
        screen.blit(font_l.render(txt_title, True, (255, 255, 255)), (50, 30))
        screen.blit(font_m.render(f"Herbe: {cg}  |  Proies: {cp}  |  Prédateurs: {cd}", True, (200, 200, 255)), (70, 65))

        # --- BLOC 2 : DYNAMIQUE (SÉPARÉ) ---
        pygame.draw.rect(screen, (40, 40, 40), (30, 120, 740, 200), border_radius=8)
        screen.blit(font_l.render("2. DYNAMIQUE DES INDIVIDUS", True, (255, 255, 255)), (50, 130))
        
        # Section Proies
        screen.blit(font_m.render("PROIES", True, (255, 255, 255)), (70, 165))
        screen.blit(font_s.render(f"- En recherche de nourriture : {ca_p}", True, (150, 255, 150)), (90, 190))
        screen.blit(font_s.render(f"- En repos / reproduction   : {max(0, cp - ca_p)}", True, (200, 255, 200)), (90, 215))
        
        # Section Prédateurs (BIEN SÉPARÉ)
        screen.blit(font_m.render("PRÉDATEURS", True, (255, 255, 255)), (420, 165))
        screen.blit(font_s.render(f"- En chasse active         : {ca_d}", True, (255, 150, 150)), (440, 190))
        screen.blit(font_s.render(f"- En phase reproduction    : {max(0, cd - ca_d)}", True, (255, 200, 200)), (440, 215))

        # --- BLOC 3 : STATS ---
        pygame.draw.rect(screen, (20, 20, 30), (30, 330, 740, 180), border_radius=8)
        screen.blit(font_l.render("3. COMPTEURS VITAUX (TOTAL)", True, (255, 255, 255)), (50, 340))
        screen.blit(font_m.render(f"Naissances : Proies [{stats['naiss_p']}] | Préd. [{stats['naiss_d']}]", True, (200, 255, 200)), (70, 385))
        screen.blit(font_m.render(f"Décès : Proies [{stats['morts_p']}] | Préd. [{stats['morts_d']}]", True, (255, 150, 150)), (70, 430))

        screen.blit(font_s.render("[D] Forcer Sécheresse | [Q] Quitter", True, (150, 150, 150)), (280, 560))
        pygame.display.flip()
        clock.tick(30)
