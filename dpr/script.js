let reminders = JSON.parse(localStorage.getItem("reminders")) || [];

// Predefined learning suggestions with links
const learningData = {
  "html": {
    topic: "Understand tags, forms, and semantic elements",
    link: "https://www.w3schools.com/html/"
  },
  "css": {
    topic: "Learn selectors, box model, and flexbox",
    link: "https://www.w3schools.com/css/"
  },
  "javascript": {
    topic: "Study variables, functions, DOM, and events",
    link: "https://developer.mozilla.org/en-US/docs/Web/JavaScript"
  },
  "python": {
    topic: "Practice syntax, loops, and functions",
    link: "https://www.w3schools.com/python/"
  },
  "java": {
    topic: "Focus on OOP, classes, and exception handling",
    link: "https://www.w3schools.com/java/"
  },
  "sql": {
    topic: "Learn SELECT, JOIN, and filtering queries",
    link: "https://www.w3schools.com/sql/"
  },
  "react": {
    topic: "Understand components, props, and state",
    link: "https://reactjs.org/learn"
  }
};

function addReminder() {
  const time = document.getElementById("reminderTime").value;
  let program = document.getElementById("reminderText").value.trim();

  if (!time || !program) {
    alert("Please fill both time and program name.");
    return;
  }

  const key = program.toLowerCase();
  const learning = learningData[key] || {
    topic: "Explore basics of this program",
    link: "https://www.google.com/search?q=" + encodeURIComponent(program + " tutorial")
  };

  reminders.push({ time, program, topic: learning.topic, link: learning.link });
  localStorage.setItem("reminders", JSON.stringify(reminders));
  displayReminders();
}

function displayReminders() {
  const list = document.getElementById("reminderList");
  list.innerHTML = "";

  reminders.forEach((reminder, index) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <div>
        <strong>${reminder.time}</strong> – ${reminder.program}<br>
        <small>📘 ${reminder.topic}</small><br>
        <a href="${reminder.link}" target="_blank">📎 Learn More</a>
      </div>
      <button onclick="deleteReminder(${index})">❌</button>
    `;
    list.appendChild(li);
  });
}

function deleteReminder(index) {
  reminders.splice(index, 1);
  localStorage.setItem("reminders", JSON.stringify(reminders));
  displayReminders();
}

setInterval(() => {
  const now = new Date();
  const currentTime = now.toTimeString().slice(0, 5); // HH:MM format

  reminders.forEach(reminder => {
    if (reminder.time === currentTime) {
      alert(`🔔 Reminder: ${reminder.program}\n📘 ${reminder.topic}\n🌐 ${reminder.link}`);
    }
  });
}, 60000);

displayReminders();
