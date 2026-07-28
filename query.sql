-- Пользователи с активной подпиской, у которых за последние 30 дней
-- нет ни одной записи в meetings_attendance.
--
-- NOT EXISTS выбран вместо LEFT JOIN + IS NULL: семантически это ровно
-- "не существует записи", план читается однозначно, и с индексом
-- idx_meetings_attendance_user_date (user_id, date) выполняется как
-- быстрый anti-join без построения промежуточного результата на всю
-- историю посещений.

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
