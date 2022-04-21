drop table if exists tb_abt_sub;
create table tb_abt_sub as
with tb_subs as (

    select t1.idPlayer,
           t1.idMedal,
           t1.dtCreatedAt,
           t1.dtExpiration,
           t1.dtRemove

    from tb_players_medalha as t1

    left join tb_medalha as t2
    on t1.idMedal = t2.idMedal

    where t2.descMedal in ("Membro Premium", "Membro Plus")
    and coalesce(t1.dtExpiration, date('now')) > t1.dtCreatedAt
)

select 
    t1.dtRef,
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
    t1.avgQtHits,
    t1.avgQtShots,
    t1.avgQtLastAlive,
    t1.avgQtClutchWon,
    t1.avgQtRoundsPlayed,
    t1.avgVlLevel,
    t1.avgQtSurvived,
    t1.avgQtTrade,
    t1.avgQtFlashAssist,
    t1.avgQtHitHeadshot,
    t1.avgQtHitChest,
    t1.avgQtHitStomach,
    t1.avgQtHitLeftArm,
    t1.avgQtHitRightArm,
    t1.avgQtHitLeftLeg,
    t1.avgQtHitRightLeg,
    t1.avgFlWinner,
    t1.propMiragePartidas,
    t1.winRateMirage,
    t1.propNukePartidas,
    t1.winRateNuke,
    t1.propInfernoPartidas,
    t1.winRateInferno,
    t1.propVertigoPartidas,
    t1.winRateVertigo,
    t1.propAncientPartidas,
    t1.winRateAncient,
    t1.propDust2Partidas,
    t1.winRateDust2,
    t1.propTrainPartidas,
    t1.winRateTrain,
    t1.propOverpassPartidas,
    t1.winRateOverpass,
    t1.vlLevelAtual,
    t1.qtMedalhaDist,
    t1.qtMedalhaAdquiridas,
    t1.qtPremium,
    t1.qtPlus,
    t1.flFacebook,
    t1.flTwitter,
    t1.flTwitch,
    t1.descCountry,
    t1.vlIdade,
    t1.vlDiasCadastro,
    case when t2.idMedal is null then 0 else 1 end as flagSub

from tb_book_players as t1

left join tb_subs as t2
on t1.idPlayer = t2.idPlayer
and t1.dtRef < t2.dtCreatedAt
and t2.dtCreatedAt < date(t1.dtRef, '+15 day')

where AssinaturaAtiva = 0
and t1.dtRef < date('2022-02-01', '-15 day')
;