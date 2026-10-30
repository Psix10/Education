package com.example.hello_spring;

import java.util.List;
import java.util.Optional;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;

@Repository
public class JdbcMessageRepository {

    private final JdbcTemplate jdbc;

    private final RowMapper<Message> mapper = (rs, rowNum) -> {
        Message message = new Message();

        message.setId(rs.getLong("id"));
        message.setContent(rs.getString("content"));
        message.setAuthorId(rs.getLong("author_id"));
        message.setCreatedAt(
                rs.getTimestamp("created_at").toLocalDateTime()
        );

        return message;
    };

    public JdbcMessageRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public Message save(CreateMessageRequest request) {
        return jdbc.queryForObject(
                """
                INSERT INTO messages (content, author_id)
                VALUES (?, ?)
                RETURNING id, content, author_id, created_at
                """,
                mapper,
                request.content(),
                request.authorId()
        );
    }

    public Optional<Message> findById(Long id) {
        return jdbc.query(
                """
                SELECT id, content, author_id, created_at
                FROM messages
                WHERE id = ?
                """,
                mapper,
                id
        ).stream().findFirst();
    }

    public List<Message> findPage(int size, long offset, Long authorId) {
        if (authorId == null) {
            return jdbc.query(
                    """
                    SELECT id, content, author_id, created_at
                    FROM messages
                    ORDER BY created_at DESC, id DESC
                    LIMIT ? OFFSET ?
                    """,
                    mapper,
                    size,
                    offset
            );
        }

        return jdbc.query(
                """
                SELECT id, content, author_id, created_at
                FROM messages
                WHERE author_id = ?
                ORDER BY created_at DESC, id DESC
                LIMIT ? OFFSET ?
                """,
                mapper,
                authorId,
                size,
                offset
        );
    }

    public long count(Long authorId) {
        if (authorId == null) {
            return jdbc.queryForObject(
                    "SELECT COUNT(*) FROM messages",
                    Long.class
            );
        }

        return jdbc.queryForObject(
                "SELECT COUNT(*) FROM messages WHERE author_id = ?",
                Long.class,
                authorId
        );
    }

    public void saveAll(List<CreateMessageRequest> requests) {
        jdbc.batchUpdate(
                "INSERT INTO messages (content, author_id) VALUES (?, ?)",
                requests,
                500,
                (ps, request) -> {
                    ps.setString(1, request.content());
                    ps.setLong(2, request.authorId());
                }
        );
    }

    public int deleteById(Long id) {
        return jdbc.update(
                "DELETE FROM messages WHERE id = ?",
                id
        );
    }
}