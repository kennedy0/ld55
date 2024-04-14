from __future__ import annotations

from typing import TYPE_CHECKING

from engine import *

if TYPE_CHECKING:
    from entities.player import Player
    from entities.blue_player import BluePlayer
    from entities.red_player import RedPlayer
    from entities.board import Board


class GameManager(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.name = "GameManager"

        # References
        self.board: Board | None = None
        self.main_menu_entities: list[Entity] = []

        # Game start
        self.board_setup_finished = False

        # Current player
        self.current_player: Player | None = None
        self.next_player: Player | None = None
        self.blue_player: BluePlayer | None = None
        self.red_player: RedPlayer | None = None

        # Turn tracking
        self.turn_ended = False

        # Between turns timer
        self.next_turn_delay = 0
        self.time_between_turns = .2
        self.turn_end_timer = 0

    def start(self) -> None:
        self.board = self.find("Board")
        self.blue_player = self.find("BluePlayer")
        self.red_player = self.find("RedPlayer")

        for entity in self.scene.entities:
            if "MainMenu" in entity.tags:
                self.main_menu_entities.append(entity)

    def update(self) -> None:
        self.update_timers()

        # Board setup
        if not self.board_setup_finished:
            if self.board.revealed_tiles == self.board.tiles_in_play:
                self.board_setup_finished = True
                self.on_board_setup_finished()

        # End Turn
        if self.turn_ended:
            self.turn_ended = False
            self.on_turn_ended()

        # Start Turn
        if not self.current_player:
            if self.turn_end_timer <= 0:
                self.on_turn_start()

    def update_timers(self) -> None:
        self.turn_end_timer -= Time.delta_time
        if self.turn_end_timer < 0:
            self.turn_end_timer = 0

    def start_game(self) -> None:
        self.hide_main_menu()

        # Do board setup
        self.board_setup_finished = False
        self.board.reveal_tiles()

    def on_board_setup_finished(self) -> None:
        # Board updates
        self.board.update_valid_tiles_for_summoning()
        self.board.set_tile_highlights()

        # Set first player
        self.next_player = self.blue_player

    def on_turn_ended(self) -> None:
        # Start in-between-turns timer
        self.turn_end_timer = self.time_between_turns + self.next_turn_delay

        # Set next player
        if self.current_player == self.blue_player:
            self.next_player = self.red_player
        else:
            self.next_player = self.blue_player

        # Unset current player
        self.current_player = None

        # Board Updates
        self.board.set_tile_highlights()

    def on_turn_start(self) -> None:
        # Set current player
        self.current_player = self.next_player
        self.next_player = None

        # Board Updates
        self.board.update_valid_tiles_for_summoning()
        self.board.set_tile_highlights()

    def on_game_end(self) -> None:
        self.show_main_menu()

    def hide_main_menu(self) -> None:
        for entity in self.main_menu_entities:
            entity.active = False

    def show_main_menu(self) -> None:
        for entity in self.main_menu_entities:
            entity.active = True
