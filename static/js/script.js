
function add_row(table, cell_data) {
    const row = table.insertRow();

    for (let i = 0; i < cell_data.length; i++) {
        const cell = row.insertCell(i);
        const data = cell_data[i];
        if (typeof data == "string")
            cell.innerHTML = data;
        else if (data instanceof Node)
            cell.appendChild(data);
        else
            console.log("Unknown column type");
    }
}

function add_completed_row(message, date_added, date_completed) {
    let table = completed_table;
    add_row(table, [message, date_added, date_completed]);
}

function add_todo_row(id, tag, message, date_added) {
    let table = null;
    
    if (tag == "need_to_do") table = need_to_do_table;
    if (tag == "want_to_do") table = want_to_do_table;
    
    if (table == null) return;
    
    let complete_button = document.createElement("button");
    complete_button.classList.add("complete-todo-button");
    complete_button.innerHTML = "✓";
    complete_button.onclick = e => complete_todo(id);
    
    let delete_button = document.createElement("button");
    delete_button.classList.add("delete-todo-button");
    delete_button.innerHTML = "×";
    delete_button.onclick = e => delete_todo(id);
    
    add_row(table, [message, date_added, complete_button, delete_button]);
}

function render_todos(data) {
    console.log(data);

    for (const todo of data) {
        let { id, tag, message, completed, date_added, date_completed } = todo;
        date_added = new Date(date_added).toDateString();
        date_completed = new Date(date_completed).toDateString();
        if (completed)
            add_completed_row(message, date_added, date_completed);
        else
            add_todo_row(id, tag, message, date_added);
    }
}

async function refresh_todos() {
    let todos = await fetch_todos();

    // clear all rows except header and input row
    while(need_to_do_table.rows.length > 2) {
        need_to_do_table.deleteRow(2);
    }

    while(want_to_do_table.rows.length > 2) {
        want_to_do_table.deleteRow(2);
    }

    while(completed_table.rows.length > 1) {
        completed_table.deleteRow(1);
    }

    render_todos(todos);
}

const tamagotchi_host = "http://192.168.0.23:5000"

const need_to_do_table = document.getElementById("need_to_do_table");
const want_to_do_table = document.getElementById("want_to_do_table");
const completed_table = document.getElementById("completed_table");

const need_to_do_input = need_to_do_table.querySelector("#todo_input");
const want_to_do_input = want_to_do_table.querySelector("#todo_input");

async function on_input_submission(e, tag) {
    if (e.key != "Enter")
        return;
    e.preventDefault();

    let message = e.target.value;
    e.target.value = "";

    if (message == "")
        return;

    submit_todo(message, tag);
}

async function fetch_todos() {
    let response = await fetch(tamagotchi_host + "/api/get_todos");
    let data = await response.json();
    if (!response.ok) return [];
    return data;
}

async function submit_todo(message, tag) {
    console.log(`Submitting todo ${message} ${tag}`);
    
    let response = await fetch(tamagotchi_host + "/api/submit_todo", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message, tag })
    });
    let data = await response.json() 

    console.log(data);
    refresh_todos();
}

async function complete_todo(id) {
    console.log(`Completing todo ${id}`);
    
    let response = await fetch(tamagotchi_host + "/api/complete_todo", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ id })
    });
    let data = await response.json() 

    console.log(data);
    refresh_todos();
}

async function delete_todo(id) {
    console.log(`Deleting todo ${id}`);
    
    let response = await fetch(tamagotchi_host + "/api/delete_todo", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ id })
    });
    let data = await response.json() 

    console.log(data);
    refresh_todos();
}

need_to_do_input.addEventListener("keydown", e => on_input_submission(e, "need_to_do"));
want_to_do_input.addEventListener("keydown", e => on_input_submission(e, "want_to_do"));

refresh_todos()

