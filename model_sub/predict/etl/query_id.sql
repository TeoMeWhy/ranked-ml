with tb_max_date as (

    select max(dtRef) as date_score
    from tb_book_players
    where idPlayer = {id_player}

)

SELECT * FROM tb_book_players

where idPlayer = {id_player}
and dtRef = (select date_score from tb_max_date)