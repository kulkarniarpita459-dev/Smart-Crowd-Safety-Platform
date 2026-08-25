import { useEffect, useState } from "react";
import "./App.css";

function App() {

  const [data, setData] = useState({
    people_count: 0,
    restricted_count: 0,
    status: "SAFE",
    date: "",
    time: ""
  });

  const [records, setRecords] = useState([]);

  // ==========================================
  // GET LIVE DATA
  // ==========================================

  const getLatestData = async () => {

    try {

      const response = await fetch(
        "http://127.0.0.1:5000/api/latest"
      );

      const result = await response.json();

      setData(result);

    } catch (error) {

      console.log("Live data error:", error);

    }
  };


  // ==========================================
  // GET DATABASE RECORDS
  // ==========================================

  const getRecords = async () => {

    try {

      const response = await fetch(
        "http://127.0.0.1:5000/api/records"
      );

      const result = await response.json();

      setRecords(result);

    } catch (error) {

      console.log("Records error:", error);

    }
  };


  // ==========================================
  // START
  // ==========================================

  useEffect(() => {

    getLatestData();
    getRecords();

    const interval = setInterval(() => {

      getLatestData();
      getRecords();

    }, 1000);

    return () => clearInterval(interval);

  }, []);


  return (

    <div className="container">

      <h1>
        Smart Crowd Safety & Intelligence Platform
      </h1>


      {/* ==========================================
          DASHBOARD CARDS
      ========================================== */}

      <div className="cards">

        <div className="card">

          <h2>👥 People Count</h2>

          <p>
            {data.people_count}
          </p>

        </div>


        <div className="card">

          <h2>🚫 Restricted Count</h2>

          <p>
            {data.restricted_count}
          </p>

        </div>


        <div className="card">

          <h2>⚠ Status</h2>

          <p
            style={{
              color:
                data.restricted_count > 0
                  ? "red"
                  : "green"
            }}
          >
            {data.status}
          </p>

        </div>

      </div>


      {/* ==========================================
          LIVE CAMERA
      ========================================== */}

      <div className="camera">

        <h2>📷 Live Camera Feed</h2>

        <img
          src="http://127.0.0.1:5000/video"
          alt="Live Camera"
          style={{
            width: "800px",
            maxWidth: "90%",
            border: "3px solid #333",
            borderRadius: "10px"
          }}
        />

      </div>


      {/* ==========================================
          DATABASE RECORDS
      ========================================== */}

      <div className="table">

        <h2>📋 Crowd Records</h2>

        <table>

          <thead>

            <tr>

              <th>Date</th>
              <th>Time</th>
              <th>People</th>
              <th>Restricted</th>
              <th>Status</th>

            </tr>

          </thead>


          <tbody>

            {records.map((record) => (

              <tr key={record.id}>

                <td>
                  {record.date}
                </td>

                <td>
                  {record.time}
                </td>

                <td>
                  {record.people_count}
                </td>

                <td>
                  {record.restricted_count}
                </td>

                <td>
                  {record.status}
                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>

    </div>

  );
}

export default App;