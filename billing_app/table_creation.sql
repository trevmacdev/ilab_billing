

drop table projects;

CREATE TABLE projects (

    id INTEGER UNSIGNED AUTO_INCREMENT NOT NULL PRIMARY KEY,
    proj_client    VARCHAR(50) NOT NULL,
	proj_name      VARCHAR(50) NOT NULL,


    -- Other columns
    po_num         VARCHAR(50) NOT NULL,
    client_manager   VARCHAR(50) NOT NULL,
    ilab_manager	VARCHAR(50) NOT NULL,
    job_code       VARCHAR(50) NOT NULL,

    manager_sig    BOOLEAN NOT NULL,
    employee_sig   BOOLEAN NOT NULL,
    notes          BOOLEAN NOT NULL,

    weekend        VARCHAR(15) NOT NULL,
    ot_rate        JSON NOT NULL,

    po_start_date      VARCHAR(10) NOT NULL,
    po_end_date		varchar(10) not null,

    -- Additional indexes
    INDEX idx_proj_client (proj_client),
    INDEX idx_proj_name (proj_name),
    INDEX idx_job_code (job_code),
    INDEX idx_ilab_manager (ilab_manager),
    INDEX idx_po_num (po_num)
)
ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

drop table employees;

CREATE TABLE employees(
	id integer unsigned auto_increment not null primary key,
    f_name varchar(50) not null,
    l_name varchar(50) not null,
    proj_client varchar(50) not null,
    proj_name varchar(50) not null,
    rate float not null,
    emp_role varchar(10) not null,
    
    -- Additional indexes
    INDEX idx_proj_client (proj_client),
    INDEX idx_proj_name (proj_name),
    INDEX idx_f_name (f_name),
    INDEX idx_l_name (l_name)
)
ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;






