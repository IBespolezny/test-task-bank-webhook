-- Пользователи с активной подпиской, у которых за последние 30 дней
-- нет ни одной записи в meetings_attendance.
--
-- NOT EXISTS выбран вместо LEFT JOIN + IS NULL чтобы не тратить ресурсы сервера впустую
-- так как ответ будет Да или Нет для определённого пользователя

SELECT u.id, u.email
FROM users u
JOIN subscriptions s ON s.user_id = u.id
WHERE s.status = 'active'
  AND s.expires_at > now()
  AND NOT EXISTS (
        SELECT 1
        FROM meetings_attendance ma
        WHERE ma.user_id = u.id
          AND ma.date >= (now() - interval '30 days')::date
  );
