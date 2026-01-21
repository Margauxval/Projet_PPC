import pygame
import sys
from pygame.locals import *

def display_process(msg_queue):
    # Initialisation de Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Simulation Écosystème - Dashboard')
    
    # Polices de caractères
    font_large = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)
    clock = pygame.time.Clock()

    last_status = "Attente de données de l'ENV..."
    logs = ["Démarrage du système graphique..."]

    while True:
        # 1. Gestion des événements Pygame (Clavier/Fenêtre)
        for event in pygame.event.get():
            if event.type == QUIT:
                msg_queue.put(("CMD", "STOP"))
                pygame.quit()
                return
            if event.type == KEYDOWN:
                if event.key == K_q:
                    # On informe l'ENV qu'il faut s'arrêter
                    msg_queue.put(("CMD", "STOP"))
                    # On ne quitte pas immédiatement ici, on attend que l'ENV renvoie "STOP"
                    # ou on quitte nous même pour fermer la fenêtre
                    pygame.quit()
                    return

        # 2. Lecture de la Queue (Données venant de l'ENV et des Agents)
        while not msg_queue.empty():
            msg = msg_queue.get()
            
            if msg == "STOP":
                pygame.quit()
                return
            
            if isinstance(msg, str):
                if "|" in msg:
                    last_status = msg # Statut global : Herbe | Proies...
                else:
                    # Log d'événement : on garde les 10 derniers
                    logs.append(msg)
                    if len(logs) > 12: logs.pop(0)

        # 3. Rendu Graphique
        screen.fill((30, 30, 30)) # Fond gris foncé

        # Section Dashboard (Haut)
        # On dessine un rectangle pour le statut
        pygame.draw.rect(screen, (50, 50, 80), (20, 20, 760, 60))
        status_surface = font_large.render(last_status, True, (255, 255, 0)) # Jaune
        screen.blit(status_surface, (40, 38))

        # Section Logs (Centre)
        title_logs = font_small.render("HISTORIQUE DES ÉVÉNEMENTS :", True, (150, 150, 150))
        screen.blit(title_logs, (40, 110))
        
        for i, log in enumerate(logs):
            # Couleur différente pour les logs importants
            color = (0, 255, 0) if "Prédation" in log else (200, 200, 200)
            log_surface = font_small.render(f"> {log}", True, color)
            screen.blit(log_surface, (50, 140 + (i * 25)))

        # Section Aide (Bas)
        footer_rect = pygame.draw.rect(screen, (20, 20, 20), (0, 560, 800, 40))
        instr = font_small.render("Contrôles : [Q] Quitter la simulation", True, (255, 255, 255))
        screen.blit(instr, (280, 572))

        pygame.display.flip()
        clock.tick(30) # Limite à 30 FPS pour économiser le CPU
