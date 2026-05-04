const checkForm = document.querySelector("#seo-check-form");
const resultPanel = document.querySelector("#result");
const scoreValue = document.querySelector("#score-value");
const scoreBar = document.querySelector("#score-bar");
const bucketTitle = document.querySelector("#bucket-title");
const bucketCopy = document.querySelector("#bucket-copy");
const recommendationsList = document.querySelector("#recommendations");
const leadForm = document.querySelector("#lead-form");
const consent = document.querySelector("#consent");
const leadSubmit = document.querySelector("#lead-submit");
const formMessage = document.querySelector("#form-message");

const hiddenScore = document.querySelector("#lead-score");
const hiddenBucket = document.querySelector("#lead-bucket");
const hiddenRecommendations = document.querySelector("#lead-recommendations");
const hiddenBranche = document.querySelector("#lead-branche");

let latestResult = null;

/*
  Scoring logic:
  Q1 Branche gives no points and is used only for recommendations.
  Q2 Stadt-Groesse: Grossstadt = 3, Mittelstadt = 2, Kleinstadt = 1.
  Q3 Sichtbarkeit: Seite 1 = 3, Manchmal = 2, Nur Name = 1, Weiss nicht = 0.
  Q4 Google Business Profile: Vollstaendig + Beitraege = 3, Selten = 2,
  Unvollstaendig = 1, Nicht vorhanden = 0.
  Q5 Bewertungen: 50+ = 3, 20-49 = 2, 5-19 = 1, 0-4 = 0.
  Total 0-12 maps to three qualitative buckets.
*/
const points = {
  citySize: {
    large: 3,
    medium: 2,
    small: 1
  },
  visibility: {
    page1: 3,
    sometimes: 2,
    nameOnly: 1,
    unknown: 0
  },
  gbp: {
    complete: 3,
    rare: 2,
    incomplete: 1,
    none: 0
  }
};

const buckets = [
  {
    min: 0,
    max: 4,
    title: "Großes Potenzial — Ihr lokales SEO startet gerade erst",
    copy: "Die Grundlagen sind noch nicht voll ausgeschöpft. Mit sauberer lokaler Sichtbarkeit, klarer Seitenstruktur und gezielten Inhalten können Sie eine bessere Basis schaffen."
  },
  {
    min: 5,
    max: 8,
    title: "Mittleres Potenzial — gezielte Optimierung kann viel bewegen",
    copy: "Es gibt bereits Ansätze, aber einige Hebel bleiben wahrscheinlich ungenutzt. Priorisierte Maßnahmen helfen dabei, Sichtbarkeit planbarer aufzubauen."
  },
  {
    min: 9,
    max: 12,
    title: "Solide Basis — jetzt die richtigen Hebel ansetzen",
    copy: "Ihre Angaben sprechen für eine gute Grundlage. Der nächste Schritt ist, die richtigen Themen, Seiten und lokalen Signale gezielt zu stärken."
  }
];

function getSelectedValue(formData, name) {
  return formData.get(name) || "";
}

function scoreReviews(value) {
  const reviews = Math.max(0, Number.parseInt(value, 10) || 0);

  if (reviews >= 50) return 3;
  if (reviews >= 20) return 2;
  if (reviews >= 5) return 1;
  return 0;
}

function getBucket(score) {
  return buckets.find((bucket) => score >= bucket.min && score <= bucket.max) || buckets[0];
}

function addUniqueRecommendation(items, text) {
  if (!items.includes(text)) {
    items.push(text);
  }
}

function buildRecommendations({ branche, visibility, gbp, reviews }) {
  const recommendations = [];

  if (gbp === "none") {
    addUniqueRecommendation(recommendations, "Google Business Profile einrichten");
  }

  if (reviews < 5) {
    addUniqueRecommendation(recommendations, "Bewertungsstrategie aufbauen");
  }

  if (visibility === "unknown") {
    addUniqueRecommendation(
      recommendations,
      branche === "Kosmetikstudio"
        ? "Google Search Console einrichten und behandlungsspezifische Keywords für Content ableiten"
        : "Google Search Console einrichten und Content-Plan ableiten"
    );
  }

  if (branche === "Kosmetikstudio") {
    addUniqueRecommendation(recommendations, "Behandlungsspezifische Keywords in eigenen Leistungsseiten abbilden");
  }

  if (gbp === "rare" || gbp === "incomplete") {
    addUniqueRecommendation(recommendations, "Google Business Profile sauber pflegen und regelmäßig aktualisieren");
  }

  if (visibility === "nameOnly" || visibility === "sometimes") {
    addUniqueRecommendation(recommendations, "Leistungsseiten auf Suchanfragen mit Stadtbezug ausrichten");
  }

  addUniqueRecommendation(recommendations, "Content-Plan für kaufnahe Suchanfragen erstellen");
  addUniqueRecommendation(recommendations, "Seitentitel, Überschriften und interne Verlinkung prüfen");
  addUniqueRecommendation(recommendations, "Lokale Wettbewerber vergleichen und Themenlücken priorisieren");

  return recommendations.slice(0, 3);
}

function updateHiddenFields(result) {
  hiddenScore.value = String(result.score);
  hiddenBucket.value = result.bucket.title;
  hiddenRecommendations.value = result.recommendations.join(" | ");
  hiddenBranche.value = result.branche;
}

function renderResult(result) {
  scoreValue.textContent = String(result.score);
  scoreBar.style.width = `${Math.round((result.score / 12) * 100)}%`;
  bucketTitle.textContent = result.bucket.title;
  bucketCopy.textContent = result.bucket.copy;
  recommendationsList.innerHTML = "";

  result.recommendations.forEach((recommendation) => {
    const item = document.createElement("li");
    item.textContent = recommendation;
    recommendationsList.appendChild(item);
  });

  resultPanel.hidden = false;
  updateHiddenFields(result);
  resultPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

checkForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const formData = new FormData(checkForm);
  const branche = getSelectedValue(formData, "branche");
  const citySize = getSelectedValue(formData, "citySize");
  const visibility = getSelectedValue(formData, "visibility");
  const gbp = getSelectedValue(formData, "gbp");
  const reviews = Math.max(0, Number.parseInt(formData.get("reviews"), 10) || 0);

  const score =
    (points.citySize[citySize] || 0) +
    (points.visibility[visibility] || 0) +
    (points.gbp[gbp] || 0) +
    scoreReviews(reviews);

  latestResult = {
    score,
    bucket: getBucket(score),
    recommendations: buildRecommendations({ branche, visibility, gbp, reviews }),
    branche
  };

  renderResult(latestResult);
});

consent.addEventListener("change", () => {
  leadSubmit.disabled = !consent.checked;
});

leadForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!latestResult || !consent.checked) {
    return;
  }

  formMessage.textContent = "";
  leadSubmit.disabled = true;

  try {
    const response = await fetch(leadForm.action, {
      method: "POST",
      body: new FormData(leadForm),
      headers: {
        Accept: "application/json"
      }
    });

    if (!response.ok) {
      throw new Error("Form submission failed");
    }

    leadForm.reset();
    updateHiddenFields(latestResult);
    leadSubmit.disabled = true;
    formMessage.textContent = "Danke — ich melde mich innerhalb von 48 Stunden mit Ihrer persönlichen Analyse.";
  } catch (error) {
    formMessage.textContent = "Die Anfrage konnte gerade nicht gesendet werden. Bitte versuchen Sie es später erneut.";
    leadSubmit.disabled = !consent.checked;
  }
});
