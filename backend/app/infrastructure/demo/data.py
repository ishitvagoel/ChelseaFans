from __future__ import annotations

from datetime import datetime

from app.domain.models import (
    ClubRef,
    DataConfidence,
    EventType,
    Match,
    MatchEvent,
    MatchStatus,
    Player,
    PlayerMatchStats,
    Score,
    SeasonTotals,
    TeamContext,
)


def _p(
    pid: str,
    name: str,
    position: str,
    number: int,
    nationality: str = "England",
) -> Player:
    return Player(
        id=pid,
        name=name,
        position=position,
        nationality=nationality,
        shirt_number=number,
    )


PALMER = _p("demo-palmer", "Cole Palmer", "Attacking Midfield", 20)
JACKSON = _p("demo-jackson", "Nicolas Jackson", "Centre-Forward", 15, "Senegal")
ENZO = _p("demo-enzo", "Enzo Fernández", "Central Midfield", 8, "Argentina")
CAICEDO = _p("demo-caicedo", "Moisés Caicedo", "Defensive Midfield", 25, "Ecuador")
SANCHEZ = _p("demo-sanchez", "Robert Sánchez", "Goalkeeper", 1, "Spain")
CUCURELLA = _p("demo-cucurella", "Marc Cucurella", "Left-Back", 3, "Spain")
COLWILL = _p("demo-colwill", "Levi Colwill", "Centre-Back", 6)
NETO = _p("demo-neto", "Pedro Neto", "Right Winger", 7, "Portugal")
JAMES = _p("demo-james", "Reece James", "Right-Back", 24)
MADUEKE = _p("demo-madueke", "Noni Madueke", "Right Winger", 11)

PLAYERS: dict[str, Player] = {
    p.id: p
    for p in (
        PALMER,
        JACKSON,
        ENZO,
        CAICEDO,
        SANCHEZ,
        CUCURELLA,
        COLWILL,
        NETO,
        JAMES,
        MADUEKE,
    )
}

CHELSEA = ClubRef(name="Chelsea", short_name="CHE")


def _stats(
    player: Player,
    *,
    minutes: int,
    goals: int | None = None,
    assists: int | None = None,
    rating: float | None = None,
    shots: int | None = None,
    key_passes: int | None = None,
    progressive_passes: int | None = None,
    progressive_carries: int | None = None,
    tackles: int | None = None,
) -> PlayerMatchStats:
    return PlayerMatchStats(
        player=player,
        minutes=minutes,
        goals=goals,
        assists=assists,
        rating=rating,
        shots=shots,
        key_passes=key_passes,
        progressive_passes=progressive_passes,
        progressive_carries=progressive_carries,
        tackles=tackles,
        source="demo",
    )


def demo_matches() -> list[Match]:
    return [
        Match(
            id="demo-2025-05-16-che-nfo",
            utc_kickoff=datetime(2025, 5, 16, 19, 0),
            competition="Premier League",
            home=CHELSEA,
            away=ClubRef("Nottingham Forest", "NFO"),
            score=Score(1, 0),
            status=MatchStatus.FINISHED,
            venue="Stamford Bridge",
            matchday=37,
            events=(
                MatchEvent(67, EventType.GOAL, "Cole Palmer", "Right-footed shot"),
                MatchEvent(88, EventType.CARD, "Moisés Caicedo", "Yellow"),
            ),
            player_stats=(
                _stats(PALMER, minutes=90, goals=1, assists=0, rating=8.4, shots=4, key_passes=3, progressive_carries=6),
                _stats(JACKSON, minutes=78, goals=0, assists=1, rating=7.2, shots=2),
                _stats(CAICEDO, minutes=90, rating=7.6, tackles=5, progressive_passes=8),
                _stats(ENZO, minutes=90, rating=7.1, key_passes=2, progressive_passes=7),
                _stats(SANCHEZ, minutes=90, rating=7.0),
            ),
            sources=(DataConfidence("demo", 0.7, "Seeded finished match for local/dev"),),
        ),
        Match(
            id="demo-2025-05-11-che-mun",
            utc_kickoff=datetime(2025, 5, 11, 15, 30),
            competition="Premier League",
            home=ClubRef("Manchester United", "MUN"),
            away=CHELSEA,
            score=Score(0, 1),
            status=MatchStatus.FINISHED,
            venue="Old Trafford",
            matchday=36,
            events=(
                MatchEvent(52, EventType.GOAL, "Enzo Fernández", "Header"),
                MatchEvent(52, EventType.ASSIST, "Reece James", None),
            ),
            player_stats=(
                _stats(ENZO, minutes=90, goals=1, rating=8.1, shots=2),
                _stats(JAMES, minutes=84, assists=1, rating=7.8, progressive_carries=4),
                _stats(PALMER, minutes=90, rating=7.4, key_passes=4, progressive_carries=5),
                _stats(COLWILL, minutes=90, rating=7.3, tackles=3),
                _stats(CUCURELLA, minutes=90, rating=7.0),
            ),
            sources=(DataConfidence("demo", 0.7, "Seeded finished match for local/dev"),),
        ),
        Match(
            id="demo-2025-05-04-che-liv",
            utc_kickoff=datetime(2025, 5, 4, 16, 30),
            competition="Premier League",
            home=CHELSEA,
            away=ClubRef("Liverpool", "LIV"),
            score=Score(3, 1),
            status=MatchStatus.FINISHED,
            venue="Stamford Bridge",
            matchday=35,
            events=(
                MatchEvent(12, EventType.GOAL, "Nicolas Jackson", None),
                MatchEvent(41, EventType.GOAL, "Cole Palmer", "Penalty"),
                MatchEvent(74, EventType.GOAL, "Pedro Neto", None),
            ),
            player_stats=(
                _stats(PALMER, minutes=90, goals=1, assists=1, rating=9.1, shots=5, key_passes=5),
                _stats(JACKSON, minutes=81, goals=1, rating=8.0, shots=3),
                _stats(NETO, minutes=88, goals=1, rating=8.2, progressive_carries=7),
                _stats(CAICEDO, minutes=90, rating=7.7, tackles=4),
                _stats(MADUEKE, minutes=70, rating=7.1, shots=2),
            ),
            sources=(DataConfidence("demo", 0.7, "Seeded finished match for local/dev"),),
        ),
        Match(
            id="demo-2025-04-26-che-ars",
            utc_kickoff=datetime(2025, 4, 26, 12, 30),
            competition="Premier League",
            home=ClubRef("Arsenal", "ARS"),
            away=CHELSEA,
            score=Score(1, 1),
            status=MatchStatus.FINISHED,
            venue="Emirates Stadium",
            matchday=34,
            events=(
                MatchEvent(33, EventType.GOAL, "Cole Palmer", None),
                MatchEvent(71, EventType.CARD, "Levi Colwill", "Yellow"),
            ),
            player_stats=(
                _stats(PALMER, minutes=90, goals=1, rating=8.0, shots=3, key_passes=2),
                _stats(CAICEDO, minutes=90, rating=7.5, tackles=6),
                _stats(COLWILL, minutes=90, rating=7.2),
                _stats(SANCHEZ, minutes=90, rating=6.9),
            ),
            sources=(DataConfidence("demo", 0.7, "Seeded finished match for local/dev"),),
        ),
        Match(
            id="demo-2025-04-20-che-ful",
            utc_kickoff=datetime(2025, 4, 20, 14, 0),
            competition="Premier League",
            home=CHELSEA,
            away=ClubRef("Fulham", "FUL"),
            score=Score(2, 1),
            status=MatchStatus.FINISHED,
            venue="Stamford Bridge",
            matchday=33,
            events=(
                MatchEvent(19, EventType.GOAL, "Noni Madueke", None),
                MatchEvent(61, EventType.GOAL, "Nicolas Jackson", None),
            ),
            player_stats=(
                _stats(MADUEKE, minutes=79, goals=1, rating=7.9, shots=3, progressive_carries=5),
                _stats(JACKSON, minutes=90, goals=1, rating=7.6, shots=4),
                _stats(ENZO, minutes=90, assists=1, rating=7.4, key_passes=3),
                _stats(CUCURELLA, minutes=90, rating=7.2),
            ),
            sources=(DataConfidence("demo", 0.7, "Seeded finished match for local/dev"),),
        ),
        Match(
            id="demo-2025-04-13-che-tot",
            utc_kickoff=datetime(2025, 4, 13, 16, 30),
            competition="Premier League",
            home=ClubRef("Tottenham Hotspur", "TOT"),
            away=CHELSEA,
            score=Score(2, 2),
            status=MatchStatus.FINISHED,
            venue="Tottenham Hotspur Stadium",
            matchday=32,
            events=(
                MatchEvent(8, EventType.GOAL, "Cole Palmer", None),
                MatchEvent(84, EventType.GOAL, "Marc Cucurella", None),
            ),
            player_stats=(
                _stats(PALMER, minutes=90, goals=1, assists=1, rating=8.3, shots=4),
                _stats(CUCURELLA, minutes=90, goals=1, rating=8.0),
                _stats(NETO, minutes=75, rating=7.0, progressive_carries=4),
                _stats(JAMES, minutes=90, rating=7.1),
            ),
            sources=(DataConfidence("demo", 0.7, "Seeded finished match for local/dev"),),
        ),
        Match(
            id="demo-2025-04-06-che-bre",
            utc_kickoff=datetime(2025, 4, 6, 14, 0),
            competition="Premier League",
            home=CHELSEA,
            away=ClubRef("Brentford", "BRE"),
            score=Score(2, 0),
            status=MatchStatus.FINISHED,
            venue="Stamford Bridge",
            matchday=31,
            events=(
                MatchEvent(29, EventType.GOAL, "Enzo Fernández", None),
                MatchEvent(77, EventType.GOAL, "Cole Palmer", None),
            ),
            player_stats=(
                _stats(PALMER, minutes=90, goals=1, rating=8.2, key_passes=4),
                _stats(ENZO, minutes=90, goals=1, rating=7.8),
                _stats(CAICEDO, minutes=90, rating=7.4, tackles=4),
            ),
            sources=(DataConfidence("demo", 0.7, "Seeded finished match for local/dev"),),
        ),
        Match(
            id="demo-2025-03-16-che-ars-fac",
            utc_kickoff=datetime(2025, 3, 16, 16, 30),
            competition="FA Cup",
            home=CHELSEA,
            away=ClubRef("Arsenal", "ARS"),
            score=Score(1, 0),
            status=MatchStatus.FINISHED,
            venue="Stamford Bridge",
            events=(MatchEvent(55, EventType.GOAL, "Reece James", "Free kick"),),
            player_stats=(
                _stats(JAMES, minutes=90, goals=1, rating=8.5),
                _stats(PALMER, minutes=90, rating=7.3, key_passes=3),
                _stats(COLWILL, minutes=90, rating=7.4),
            ),
            sources=(DataConfidence("demo", 0.7, "Seeded finished match for local/dev"),),
        ),
    ]


def demo_season_totals() -> list[SeasonTotals]:
    def row(
        player: Player,
        season: str,
        *,
        apps: int,
        minutes: int,
        goals: int,
        assists: int,
        rating: float,
        prog_p: int | None = None,
        prog_c: int | None = None,
        competition: str = "Premier League",
    ) -> SeasonTotals:
        return SeasonTotals(
            player=player,
            season=season,
            competition=competition,
            appearances=apps,
            minutes=minutes,
            goals=goals,
            assists=assists,
            rating=rating,
            progressive_passes=prog_p,
            progressive_carries=prog_c,
            source="demo",
        )

    return [
        row(PALMER, "2024/25", apps=37, minutes=3120, goals=15, assists=10, rating=7.62, prog_p=142, prog_c=98),
        row(PALMER, "2023/24", apps=34, minutes=2610, goals=22, assists=11, rating=7.81, prog_p=128, prog_c=110),
        row(JACKSON, "2024/25", apps=30, minutes=2140, goals=10, assists=5, rating=6.92, prog_c=64),
        row(JACKSON, "2023/24", apps=35, minutes=2801, goals=14, assists=5, rating=6.88, prog_c=71),
        row(ENZO, "2024/25", apps=36, minutes=3012, goals=6, assists=7, rating=7.21, prog_p=210),
        row(ENZO, "2023/24", apps=28, minutes=2204, goals=3, assists=2, rating=7.05, prog_p=156),
        row(CAICEDO, "2024/25", apps=38, minutes=3320, goals=1, assists=3, rating=7.28, prog_p=188),
        row(CAICEDO, "2023/24", apps=35, minutes=3011, goals=1, assists=3, rating=7.11, prog_p=164),
        row(NETO, "2024/25", apps=35, minutes=2450, goals=8, assists=8, rating=7.18, prog_c=121),
        row(MADUEKE, "2024/25", apps=32, minutes=1988, goals=7, assists=5, rating=7.02, prog_c=88),
        row(MADUEKE, "2023/24", apps=23, minutes=1210, goals=5, assists=2, rating=6.91, prog_c=52),
        row(JAMES, "2024/25", apps=19, minutes=1412, goals=3, assists=4, rating=7.35, prog_p=90),
        row(JAMES, "2023/24", apps=10, minutes=702, goals=0, assists=2, rating=7.14, prog_p=41),
        row(CUCURELLA, "2024/25", apps=34, minutes=2890, goals=2, assists=3, rating=7.09),
        row(COLWILL, "2024/25", apps=33, minutes=2888, goals=1, assists=1, rating=7.12),
        row(SANCHEZ, "2024/25", apps=32, minutes=2880, goals=0, assists=0, rating=6.84),
    ]


def demo_team_context() -> TeamContext:
    return TeamContext(
        team_name="Chelsea",
        competition="Premier League",
        position=4,
        played=38,
        points=69,
        form="WWDWL",
        goal_difference=22,
        sources=(DataConfidence("demo", 0.65, "Illustrative table snapshot"),),
    )
