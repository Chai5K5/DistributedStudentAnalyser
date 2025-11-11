-- ======================================================================
-- DISTRIBUTED STUDENT DATABASE SYSTEM (MySQL Backend)
-- Author: Chaitanya Sharma
-- Description: Implements distributed CRUD operations, predicate pushdown,
--              and replication triggers using pure MySQL.
-- ======================================================================

-- ---------- 1. CENTRAL COORDINATOR DATABASE ----------
CREATE DATABASE IF NOT EXISTS db_catalog;
USE db_catalog;

-- ======================================================================
-- 2. UNIFIED VIEW (Horizontal Fragmentation)
-- ======================================================================
DROP VIEW IF EXISTS all_students;
CREATE VIEW all_students AS
SELECT * FROM db_cse.students
UNION ALL
SELECT * FROM db_aiml.students
UNION ALL
SELECT * FROM db_ds.students
UNION ALL
SELECT * FROM db_cc.students;

-- ======================================================================
-- 3. STORED PROCEDURES
-- ======================================================================

DELIMITER $$

-- ---------------------- ADD STUDENT ----------------------
DROP PROCEDURE IF EXISTS add_student $$
CREATE PROCEDURE add_student (
  IN p_roll INT,
  IN p_name VARCHAR(100),
  IN p_branch VARCHAR(20),
  IN p_marks FLOAT,
  IN p_att FLOAT
)
BEGIN
  DECLARE db_name VARCHAR(30);

  SET db_name = CASE
    WHEN UPPER(p_branch) = 'CSE' THEN 'db_cse'
    WHEN UPPER(p_branch) = 'AIML' THEN 'db_aiml'
    WHEN UPPER(p_branch) = 'DS' THEN 'db_ds'
    WHEN UPPER(p_branch) = 'CC' THEN 'db_cc'
    ELSE NULL END;

  IF db_name IS NOT NULL THEN
    SET @sql = CONCAT('INSERT INTO ', db_name,
                      '.students VALUES (?, ?, ?, ?, ?)');

    SET @v_roll = p_roll;
    SET @v_name = p_name;
    SET @v_branch = p_branch;
    SET @v_marks = p_marks;
    SET @v_att = p_att;

    PREPARE ps FROM @sql;
    EXECUTE ps USING @v_roll, @v_name, @v_branch, @v_marks, @v_att;
    DEALLOCATE PREPARE ps;
  ELSE
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Invalid branch specified!';
  END IF;
END $$


-- ---------------------- UPDATE STUDENT ----------------------
DROP PROCEDURE IF EXISTS update_student $$
CREATE PROCEDURE update_student (
  IN p_roll INT,
  IN p_branch VARCHAR(20),
  IN p_marks FLOAT,
  IN p_att FLOAT
)
BEGIN
  SET @sql = CONCAT(
    'UPDATE ',
    CASE UPPER(p_branch)
      WHEN 'CSE' THEN 'db_cse'
      WHEN 'AIML' THEN 'db_aiml'
      WHEN 'DS' THEN 'db_ds'
      WHEN 'CC' THEN 'db_cc'
    END,
    '.students SET marks = ?, attendance = ? WHERE roll_no = ?'
  );

  SET @v_marks = p_marks;
  SET @v_att = p_att;
  SET @v_roll = p_roll;

  PREPARE ps FROM @sql;
  EXECUTE ps USING @v_marks, @v_att, @v_roll;
  DEALLOCATE PREPARE ps;
END $$


-- ---------------------- DELETE STUDENT ----------------------
DROP PROCEDURE IF EXISTS delete_student $$
CREATE PROCEDURE delete_student (
  IN p_roll INT,
  IN p_branch VARCHAR(20)
)
BEGIN
  SET @sql = CONCAT(
    'DELETE FROM ',
    CASE UPPER(p_branch)
      WHEN 'CSE' THEN 'db_cse'
      WHEN 'AIML' THEN 'db_aiml'
      WHEN 'DS' THEN 'db_ds'
      WHEN 'CC' THEN 'db_cc'
    END,
    '.students WHERE roll_no = ?'
  );

  SET @v_roll = p_roll;

  PREPARE ps FROM @sql;
  EXECUTE ps USING @v_roll;
  DEALLOCATE PREPARE ps;
END $$


-- ======================================================================
-- 4. FILTER STUDENTS (Predicate Pushdown)
-- ======================================================================
DROP PROCEDURE IF EXISTS filter_students $$
CREATE PROCEDURE filter_students (
  IN p_branch VARCHAR(20),
  IN p_marks_min FLOAT,
  IN p_marks_max FLOAT,
  IN p_att_min FLOAT,
  IN p_att_max FLOAT
)
BEGIN
  DECLARE where_clause TEXT DEFAULT ' WHERE 1=1 ';
  DECLARE sql_text TEXT;

  IF p_marks_min IS NOT NULL THEN
    SET where_clause = CONCAT(where_clause, ' AND marks >= ', p_marks_min);
  END IF;
  IF p_marks_max IS NOT NULL THEN
    SET where_clause = CONCAT(where_clause, ' AND marks <= ', p_marks_max);
  END IF;
  IF p_att_min IS NOT NULL THEN
    SET where_clause = CONCAT(where_clause, ' AND attendance >= ', p_att_min);
  END IF;
  IF p_att_max IS NOT NULL THEN
    SET where_clause = CONCAT(where_clause, ' AND attendance <= ', p_att_max);
  END IF;

  IF p_branch IS NOT NULL AND p_branch <> '' THEN
    SET sql_text = CONCAT('SELECT * FROM ', 'db_', LOWER(p_branch), '.students', where_clause);
  ELSE
    SET sql_text = CONCAT(
      'SELECT * FROM db_cse.students', where_clause,
      ' UNION ALL SELECT * FROM db_aiml.students', where_clause,
      ' UNION ALL SELECT * FROM db_ds.students', where_clause,
      ' UNION ALL SELECT * FROM db_cc.students', where_clause
    );
  END IF;

  SET @query = sql_text;
  PREPARE stmt FROM @query;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;
END $$


-- ======================================================================
-- 5. SEARCH STUDENTS (Name / Marks Filter)
-- ======================================================================
DROP PROCEDURE IF EXISTS search_students $$
CREATE PROCEDURE search_students (
  IN p_keyword VARCHAR(100),
  IN p_min_marks FLOAT,
  IN p_max_marks FLOAT,
  IN p_branch VARCHAR(20)
)
BEGIN
  DECLARE sql_text TEXT DEFAULT '';
  DECLARE where_clause TEXT DEFAULT ' WHERE 1=1 ';

  IF p_keyword IS NOT NULL AND p_keyword <> '' THEN
    SET where_clause = CONCAT(where_clause, " AND name LIKE '%", p_keyword, "%'");
  END IF;
  IF p_min_marks IS NOT NULL THEN
    SET where_clause = CONCAT(where_clause, ' AND marks >= ', p_min_marks);
  END IF;
  IF p_max_marks IS NOT NULL THEN
    SET where_clause = CONCAT(where_clause, ' AND marks <= ', p_max_marks);
  END IF;

  IF p_branch IS NOT NULL AND p_branch <> '' THEN
    SET sql_text = CONCAT('SELECT * FROM ', 'db_', LOWER(p_branch), '.students', where_clause);
  ELSE
    SET sql_text = CONCAT(
      'SELECT * FROM db_cse.students', where_clause,
      ' UNION ALL SELECT * FROM db_aiml.students', where_clause,
      ' UNION ALL SELECT * FROM db_ds.students', where_clause,
      ' UNION ALL SELECT * FROM db_cc.students', where_clause
    );
  END IF;

  SET @query = sql_text;
  PREPARE stmt FROM @query;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;
END $$


-- ======================================================================
-- 6. REPLICATION TRIGGER (CSE → AIML)
-- ======================================================================
USE db_cse $$

DROP TRIGGER IF EXISTS trg_cse_rep $$
CREATE TRIGGER trg_cse_rep
AFTER INSERT ON students
FOR EACH ROW
BEGIN
  REPLACE INTO db_aiml.students (roll_no, name, branch, marks, attendance)
  VALUES (NEW.roll_no, NEW.name, NEW.branch, NEW.marks, NEW.attendance);
END $$

DELIMITER ;

-- ======================================================================
-- ✅ END OF FILE: distributed_backend.sql
-- ======================================================================
