/* ##### BEGINNING ##### */

document.addEventListener("DOMContentLoaded", () => {
  console.log("F1 app loaded!");
  loadSeason();
  renderTabsBar();
  document.getElementById("navStandings").classList.add("active");

  document.getElementById("navStandings").addEventListener("click", () => {
    document.getElementById("tabsBar").style.display = "flex";
    const allNavs = document.querySelectorAll(".nav-link");
    for (const n of allNavs) {
      n.classList.remove("active");
    }
    document.getElementById("navStandings").classList.add("active");
    const season = document.getElementById("seasonSelect").value;
    if (currentTab === "Drivers") {
      loadStandingsDrivers(season);
    } else {
      loadStandingsTeams(season);
    }
  });

  document.getElementById("navResults").addEventListener("click", () => {
    document.getElementById("tabsBar").style.display = "none";
    const allNavs = document.querySelectorAll(".nav-link");
    for (const n of allNavs) {
      n.classList.remove("active");
    }
    document.getElementById("navResults").classList.add("active");
    const season = document.getElementById("seasonSelect").value;
    document.getElementById("content").innerHTML = "<h1>Round Results Soon</h1>";
  });
});

/* ##### VARIABLES AND UTILITIES ##### */
let currentTab = "Drivers";

function badge(position) {
  const pos = Number(position);
  if (pos === 1) {
    return '<span class="badge pos-1">1</span>';
  } else if (pos === 2) {
    return '<span class="badge pos-2">2</span>';
  } else if (pos === 3) {
    return '<span class="badge pos-3">3</span>';
  }
  return `<span class="badge">${pos}</span>`;
}

/* ##### MENU - TABS ##### */

async function renderTabsBar() {
  const tabBar = document.getElementById("tabsBar");
  const tabs = ["Drivers", "Teams"];
  for (const i of tabs) {
    const tab = document.createElement("div");
    tab.textContent = i;
    tab.className = "tab";
    tabBar.appendChild(tab);
    if (i === currentTab) {
      tab.classList.add("active");
    }
    tab.addEventListener("click", () => {
      const allTabs = document.querySelectorAll(".tab");
      for (const t of allTabs) {
        t.classList.remove("active");
      }
      tab.classList.add("active");
      currentTab = i;
      const season = document.getElementById("seasonSelect").value;
      console.log(i);
      if (i === "Drivers") {
        loadStandingsDrivers(season);
      } else {
        loadStandingsTeams(season);
      }
    });
  }
}

async function loadSeason() {
  const response = await fetch("/api/seasons");
  const seasons = await response.json();

  const select = document.getElementById("seasonSelect");
  select.innerHTML = "";

  for (const season of seasons) {
    const option = document.createElement("option");
    option.value = season;
    option.textContent = season;
    select.appendChild(option);
  }
  select.addEventListener("change", () => {
    if (currentTab === "Drivers") {
      loadStandingsDrivers(select.value);
    } else {
      loadStandingsTeams(select.value);
    }
  });

  loadStandingsDrivers(select.value);
}

async function loadStandingsDrivers(season) {
  const response = await fetch(`/api/standings/drivers?season=${season}`);
  const data = await response.json();
  const content = document.getElementById("content");
  let rowsHTML = "";
  content.innerHTML = "";
  for (const row of data.rows) {
    rowsHTML += `
    <tr>
      <td>${badge(row.position)}</td>
      <td><img class="avatar" src="${row.driver.photo}"> <a href="/driver/${row.driver.id}?season=${season}">${row.driver.givenName}${row.driver.familyName}</a></td>
      <td><img class="flagimg" src="${row.driver.flag}"></td>
      <td><img class="avatar" src="${row.team.photo}"> <a href="/team/${row.team.id}?season=${season}"> ${row.team.name}</a></td>
      <td>${row.points}</td>
      <td>${row.wins}</td>
    </tr>`;
  }
  content.innerHTML += `
    <h2 class="view-title"> ${season} Driver Standing</h2>
    <div class="tablewrap">
    <table>
      <thead>
        <tr>
          <th>POS</th>
          <th>DRIVER</th>
          <th>NAT</th>
          <th>TEAM</th>
          <th>PTS</th>
          <th>WINS</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHTML}
      </tbody>
    </table>
    </div>`;
  console.log(data);
}

async function loadStandingsTeams(season) {
  const response = await fetch(`/api/standings/teams?season=${season}`);
  const data = await response.json();
  const content = document.getElementById("content");
  let rowsHTML = "";
  content.innerHTML = "";
  for (const row of data.rows) {
    rowsHTML += `
    <tr>
      <td>${badge(row.position)}</td>
      <td><img class="avatar" src="${row.team.photo}"><a href="/team/${row.team.id}?season=${season}">${row.team.name}</a></td>
      <td><img class="flagimg" src="${row.team.flag}"></td>
      <td>${row.points}</td>
      <td>${row.wins}</td>
    </tr>`;
  }
  content.innerHTML += `
    <h2 class="view-title"> ${season} Team Standing</h2>
    <div class="tablewrap">
    <table>
      <thead>
        <tr>
          <th>POS</th>
          <th>TEAM</th>
          <th>NAT</th>
          <th>PTS</th>
          <th>WINS</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHTML}
      </tbody>
    </table>
    </div>`;
  console.log(data);
}
