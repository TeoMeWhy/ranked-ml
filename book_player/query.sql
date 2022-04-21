with tb_lobby as (

    select *
    from tb_lobby_stats_player
    where dtCreatedAt < '{date}'
    and dtCreatedAt > date('{date}', '-30 day')

),

tb_stats as (

    select idPlayer,
            count(distinct idLobbyGame) as qtPartidas,
            count(distinct case when qtRoundsPlayed < 16 then idLobbyGame end) as qtPartidasMenos16,
            count(distinct date(dtCreatedAt)) as qtDias,
            min( julianday('{date}') - julianday(dtCreatedAt) ) as qtDiasUltimaLobby,
            1.0 * count(distinct idLobbyGame) / count(distinct date(dtCreatedAt)) as mediaPartidasDia,
            avg(qtKill) as avgQtKill,
            avg(qtAssist) as avgQtAssist,
            avg(qtDeath) as avgQtDeath,
            avg(1.0 * (qtKill + qtAssist) / coalesce(qtDeath,1)) as avgKDA,
            coalesce(1.0 * sum(qtKill + qtAssist)/sum(coalesce(qtDeath,1)),0) as KDAgeral,
            avg(1.0*(qtKill + qtAssist)/qtRoundsPlayed) as avgKARound,
            1.0 * sum(qtKill + qtAssist)/sum(qtRoundsPlayed) as KARoundGeral,
            avg(qtHs) as avgQtHs,
            coalesce(avg(1.0 * qtHs/ qtKill),0) as avgHsRate,
            coalesce(1.0 * sum(qtHs) / sum(qtKill),0) as txHsGeral,
            avg(qtBombeDefuse) as avgQtBombeDefuse,
            avg(qtBombePlant) as avgQtBombePlant,
            avg(qtTk) as avgQtTk,
            avg(qtTkAssist) as avgQtTkAssist,
            avg(qt1Kill) as avgQt1Kill,
            avg(qt2Kill) as avgQt2Kill,
            avg(qt3Kill) as avgQt3Kill,
            avg(qt4Kill) as avgQt4Kill,
            sum(qt4Kill) as sumQt4Kill,
            avg(qt5Kill) as avgQt5Kill,
            sum(qt5Kill) as sumQt5Kill,
            avg(qtPlusKill) as avgQtPlusKill,
            avg(qtFirstKill) as avgQtFirstKill,
            avg(vlDamage) as avgVlDamage,
            avg(1.0 * vlDamage/qtRoundsPlayed) as avgDamageRound,
            1.0 * sum(vlDamage) / sum(qtRoundsPlayed) as DamageRoundGeral,
            avg(qtHits) as avgQtHits,
            avg(qtShots) as avgQtShots,
            avg(qtLastAlive) as avgQtLastAlive,
            avg(qtClutchWon) as avgQtClutchWon,
            avg(qtRoundsPlayed) as avgQtRoundsPlayed,
            avg(vlLevel) as avgVlLevel,
            coalesce(avg(qtSurvived),0) as avgQtSurvived,
            avg(qtTrade) as avgQtTrade,
            coalesce(avg(qtFlashAssist),0) as avgQtFlashAssist,
            coalesce(avg(qtHitHeadshot),0) as avgQtHitHeadshot,
            coalesce(avg(qtHitChest),0) as avgQtHitChest,
            coalesce(avg(qtHitStomach),0) as avgQtHitStomach,
            coalesce(avg(qtHitLeftAtm),0) as avgQtHitLeftArm,
            coalesce(avg(qtHitRightArm),0) as avgQtHitRightArm,
            coalesce(avg(qtHitLeftLeg),0) as avgQtHitLeftLeg,
            coalesce(avg(qtHitRightLeg),0) as avgQtHitRightLeg,
            avg(flWinner) as avgFlWinner,
            count( distinct case when descMapName = "de_mirage" then idLobbyGame end) as qtMiragePartidas,
            count( distinct case when descMapName = "de_mirage" and flWinner = 1 then idLobbyGame end) as qtMirageVitorias,
            count( distinct case when descMapName = "de_nuke" then idLobbyGame end) as qtNukePartidas,
            count( distinct case when descMapName = "de_nuke" and flWinner = 1 then idLobbyGame end) as qtNukeVitorias,
            count( distinct case when descMapName = "de_inferno" then idLobbyGame end) as qtInfernoPartidas,
            count( distinct case when descMapName = "de_inferno" and flWinner = 1 then idLobbyGame end) as qtInfernoVitorias,
            count( distinct case when descMapName = "de_vertigo" then idLobbyGame end) as qtVertigoPartidas,
            count( distinct case when descMapName = "de_vertigo" and flWinner = 1 then idLobbyGame end) as qtVertigoVitorias,
            count( distinct case when descMapName = "de_ancient" then idLobbyGame end) as qtAncientPartidas,
            count( distinct case when descMapName = "de_ancient" and flWinner = 1 then idLobbyGame end) as qtAncientVitorias,
            count( distinct case when descMapName = "de_dust2" then idLobbyGame end) as qtDust2Partidas,
            count( distinct case when descMapName = "de_dust2" and flWinner = 1 then idLobbyGame end) as qtDust2Vitorias,
            count( distinct case when descMapName = "de_train" then idLobbyGame end) as qtTrainPartidas,
            count( distinct case when descMapName = "de_train" and flWinner = 1 then idLobbyGame end) as qtTrainVitorias,
            count( distinct case when descMapName = "de_overpass" then idLobbyGame end) as qtOverpassPartidas,
            count( distinct case when descMapName = "de_overpass" and flWinner = 1 then idLobbyGame end) as qtOverpassVitorias

    from tb_lobby

    group by idPlayer
),

tb_lvl_atual as (

    select idPlayer,
           vlLevel
    from( 
        select idLobbyGame,
               idPlayer,
               vlLevel,
               dtCreatedAt,
               row_number() over (PARTITION by idPlayer order by dtCreatedAt desc) as rn
        from tb_lobby
    )
    where rn = 1
),

tb_book_lobby as (
    select t1.*,
        t2.vlLevel as vlLevelAtual

    from tb_stats as t1

    left join tb_lvl_atual as t2
    on t1.idPlayer = t2.idPlayer
),

tb_medals as (

    select *
    from tb_players_medalha as t1

    left join tb_medalha as t2
    on t1.idMedal = t2.idMedal

    where dtCreatedAt < dtExpiration
    and dtCreatedAt < '{date}'
    and coalesce(dtRemove, dtExpiration) > date('{date}', '-30 day')

),

tb_book_medal as (

    select idPlayer,
            count(DISTINCT idMedal) as qtMedalhaDist,
            count( distinct case when dtCreatedAt > date('{date}', '-30 day') then id end) as qtMedalhaAdquiridas,
            sum(case when descMedal = 'Membro Premium' then 1 else 0 end) as qtPremium,
            sum(case when descMedal = 'Membro Plus' then 1 else 0 end) as qtPlus,
            max( case when descMedal in ('Membro Premium', 'Membro Plus')
                           and coalesce(dtRemove, dtExpiration) >= '{date}'
                      then 1 else 0 end ) as AssinaturaAtiva

    from tb_medals
    group by idPlayer

)

insert into tb_book_players

select '{date}' as dtRef,
        t1.idPlayer,
        t1.qtPartidas,
        t1.qtPartidasMenos16,
        t1.qtDias,
        t1.qtDiasUltimaLobby,
        t1.mediaPartidasDia,
        t1.avgQtKill,
        t1.avgQtAssist,
        t1.avgQtDeath,
        t1.avgKDA,
        t1.KDAgeral,
        t1.avgKARound,
        t1.KARoundGeral,
        t1.avgQtHs,
        t1.avgHsRate,
        t1.txHsGeral,
        t1.avgQtBombeDefuse,
        t1.avgQtBombePlant,
        t1.avgQtTk,
        t1.avgQtTkAssist,
        t1.avgQt1Kill,
        t1.avgQt2Kill,
        t1.avgQt3Kill,
        t1.avgQt4Kill,
        t1.sumQt4Kill,
        t1.avgQt5Kill,
        t1.sumQt5Kill,
        t1.avgQtPlusKill,
        t1.avgQtFirstKill,
        t1.avgVlDamage,
        t1.avgDamageRound,
        t1.DamageRoundGeral,
        t1.avgQtShots,
        t1.avgQtLastAlive,
        t1.avgQtClutchWon,
        t1.avgQtHits,
        t1.avgQtRoundsPlayed,
        t1.avgVlLevel,
        t1.avgQtSurvived,
        coalesce(t1.avgQtTrade,0),
        t1.avgQtFlashAssist,
        t1.avgQtHitHeadshot,
        t1.avgQtHitChest,
        t1.avgQtHitStomach,
        t1.avgQtHitLeftArm,
        t1.avgQtHitRightArm,
        t1.avgQtHitLeftLeg,
        t1.avgQtHitRightLeg,
        t1.avgFlWinner,
        t1.qtMiragePartidas / t1.qtPartidas as propMiragePartidas,
        t1.qtMirageVitorias  / t1.qtMiragePartidas as winRateMirage,
        t1.qtNukePartidas / t1.qtPartidas as propNukePartidas,
        t1.qtNukeVitorias  / t1.qtNukePartidas as winRateNuke,
        t1.qtInfernoPartidas / t1.qtPartidas as propInfernoPartidas,
        t1.qtInfernoVitorias  / t1.qtInfernoPartidas as winRateInferno,
        t1.qtVertigoPartidas / t1.qtPartidas as propVertigoPartidas,
        t1.qtVertigoVitorias  / t1.qtVertigoPartidas as winRateVertigo,
        t1.qtAncientPartidas / t1.qtPartidas as propAncientPartidas,
        t1.qtAncientVitorias  / t1.qtAncientPartidas as winRateAncient,
        t1.qtDust2Partidas / t1.qtPartidas as propDust2Partidas,
        t1.qtDust2Vitorias  / t1.qtDust2Partidas as winRateDust2,
        t1.qtTrainPartidas / t1.qtPartidas as propTrainPartidas,
        t1.qtTrainVitorias  / t1.qtTrainPartidas as winRateTrain,
        t1.qtOverpassPartidas / t1.qtPartidas as propOverpassPartidas,
        t1.qtOverpassVitorias / t1.qtOverpassPartidas as winRateOverpass,
        t1.vlLevelAtual,
       coalesce(t2.qtMedalhaDist,0) as qtMedalhaDist,
       coalesce(t2.qtMedalhaAdquiridas,0) as qtMedalhaAdquiridas,
       coalesce(t2.qtPremium,0) as qtPremium,
       coalesce(t2.qtPlus,0) as qtPlus,
       coalesce(t2.AssinaturaAtiva,0) as AssinaturaAtiva,
       t3.flFacebook,
       t3.flTwitter,
       t3.flTwitch,
       t3.descCountry,
       ((JulianDay('{date}')) - JulianDay(t3.dtBirth))/365.25 as vlIdade,
       (JulianDay('{date}')) - JulianDay(t3.dtRegistration) as vlDiasCadastro

from tb_book_lobby as t1

left join tb_book_medal as t2
on t1.idPlayer = t2.idPlayer

left join tb_players as t3
on t1.idPlayer = t3.idPlayer;