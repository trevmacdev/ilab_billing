
DELIMITER $$

CREATE PROCEDURE si_get_projects_clients()
BEGIN
    SELECT
        proj_client,
        proj_name
    FROM projects
    ORDER BY proj_client, proj_name;
END$$

CREATE PROCEDURE si_delete_project(
	IN i_proj_client varchar(50),
    IN i_proj_name	varchar(50)
)
BEGIN
	DELETE
    FROM projects
    WHERE 
		proj_client = i_proj_client
	AND
		proj_name = i_proj_name;
END $$

CREATE PROCEDURE si_get_project_details(
	IN i_proj_client varchar(50),
    IN i_proj_name	varchar(50)
)
BEGIN
	SELECT *
    FROM projects
    WHERE 
		proj_client = i_proj_client
    AND
		proj_name = i_proj_name;    
END $$


CREATE PROCEDURE sp_create_employee_insert(
    in i_f_name varchar(50),
    in i_l_name varchar(50),
    in i_proj_client varchar(50),
    in i_proj_name varchar(50),
    in i_rate float,
    in i_emp_role varchar(10)
)
BEGIN
	INSERT INTO employees(
		f_name,
		l_name,
		proj_client,
		proj_name,
		rate,
		emp_role
    )
    VALUES(
		i_f_name,
		i_l_name,
		i_proj_client,
		i_proj_name,
		i_rate,
		i_emp_role
    );
END $$

CREATE PROCEDURE sp_create_project_insert (
    IN i_proj_client   VARCHAR(50),
    IN i_proj_name     VARCHAR(50),
    IN i_po_num        VARCHAR(50),
    IN i_client_manager VARCHAR(50),
    IN i_ilab_manager  VARCHAR(50),
    IN i_job_code      VARCHAR(50),
    IN i_manager_sig   BOOLEAN,
    IN i_employee_sig  BOOLEAN,
    IN i_notes         BOOLEAN,
    IN i_weekend       VARCHAR(15),
    IN i_ot_rate       JSON,
    IN i_po_start_date VARCHAR(10),
    IN i_po_end_date   VARCHAR(10)
)
BEGIN
    INSERT INTO projects (
        proj_client,
        proj_name,
        po_num,
        client_manager,
        ilab_manager,
        job_code,
        manager_sig,
        employee_sig,
        notes,
        weekend,
        ot_rate,
        po_start_date,
        po_end_date
    )
    VALUES (
        i_proj_client,
        i_proj_name,
        i_po_num,
        i_client_manager,
        i_ilab_manager,
        i_job_code,
        i_manager_sig,
        i_employee_sig,
        i_notes,
        i_weekend,
        i_ot_rate,
        i_po_start_date,
        i_po_end_date
    );

END$$



DELIMITER ;
