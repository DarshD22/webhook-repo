import React, { useEffect, useState } from 'react';

function App() {
  const [events, setEvents] = useState([]);

  const fetchEvents = async () => {
    try {
      const res = await fetch("https://webhook-repo-8ccs.onrender.com/events");
      const data = await res.json();
      setEvents(data);
    } catch (err) {
      console.error("Error fetching events:", err);
    }
  };

  useEffect(() => {
    fetchEvents(); // initial load
    const interval = setInterval(fetchEvents, 15000); // poll every 15s
    return () => clearInterval(interval);
  }, []);

  const renderMessage = (event) => {
    const { action, author, from_branch, to_branch, timestamp } = event;

    if (action === "push") {
      return `${author} pushed to ${to_branch} on ${timestamp}`;
    } else if (action === "pull_request") {
      return `${author} submitted a pull request from ${from_branch} to ${to_branch} on ${timestamp}`;
    } else if (action === "merge") {
      return `${author} merged branch ${from_branch} to ${to_branch} on ${timestamp}`;
    }
    return "Unknown event";
  };

  return (
    <div style={{ padding: "30px", fontFamily: "Arial" }}>
      <h2>GitHub Activity Feed</h2>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {events.map((e, index) => (
          <li key={index} style={{ margin: "10px 0" }}>
            {renderMessage(e)}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
