package com.example.hello_spring;

import java.util.Optional;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class JdbcUserRepository {

    private final JdbcTemplate jdbc;

    public JdbcUserRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public User save(String username) {
        return jdbc.queryForObject(
                """
                INSERT INTO users (username)
                VALUES (?)
                RETURNING id, username
                """,
                (rs, rowNum) -> new User(
                        rs.getLong("id"),
                        rs.getString("username")
                ),
                username
        );
    }

    public Optional<User> findById(Long id) {
        return jdbc.query(
                "SELECT id, username FROM users WHERE id = ?",
                (rs, rowNum) -> new User(
                        rs.getLong("id"),
                        rs.getString("username")
                ),
                id
        ).stream().findFirst();
    }
}