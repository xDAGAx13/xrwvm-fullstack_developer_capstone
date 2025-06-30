const express  = require('express');
const mongoose = require('mongoose');
const fs       = require('fs');
const cors     = require('cors');

const app  = express();
const port = 3030;

app.use(cors());
app.use(require('body-parser').urlencoded({ extended: false }));

const reviews_data     = JSON.parse(fs.readFileSync('reviews.json',     'utf8'));
const dealerships_data = JSON.parse(fs.readFileSync('dealerships.json', 'utf8'));

mongoose.connect('mongodb://mongo_db:27017/', { dbName: 'dealershipsDB' });

const Reviews      = require('./review');
const Dealerships  = require('./dealership');

/* ---------- seed the collections whenever the container starts ---------- */
(async () => {
  try {
    await Reviews.deleteMany({});
    await Reviews.insertMany(reviews_data.reviews);

    await Dealerships.deleteMany({});
    await Dealerships.insertMany(dealerships_data.dealerships);
  } catch (error) {
    console.error('Error seeding data:', error);
  }
})();

/* ---------------------------- ROUTES ----------------------------------- */

// Home
app.get('/', (_, res) => {
  res.send('Welcome to the Mongoose API');
});

/* ---------- Review endpoints ---------- */

app.get('/fetchReviews', async (_, res) => {
  try {
    const documents = await Reviews.find();
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

app.get('/fetchReviews/dealer/:id', async (req, res) => {
  try {
    const documents = await Reviews.find({ dealership: req.params.id });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

/* ---------- Dealership endpoints ---------- */

/* 1. Fetch ALL dealerships */
app.get('/fetchDealers', async (_, res) => {
  try {
    const documents = await Dealerships.find();
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

/* 2. Fetch dealerships BY STATE (case-insensitive) */
app.get('/fetchDealers/:state', async (req, res) => {
  try {
    const state = req.params.state.toUpperCase();      // normalise input
    const documents = await Dealerships.find({ state });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

/* 3. Fetch a single dealer BY ID */
app.get('/fetchDealer/:id', async (req, res) => {
  try {
    const dealer = await Dealerships.findOne({ id: Number(req.params.id) });
    if (!dealer) {
      return res.status(404).json({ error: 'Dealer not found' });
    }
    res.json(dealer);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

/* ---------- Insert review ---------- */
app.post('/insert_review', express.raw({ type: '*/*' }), async (req, res) => {
  const data     = JSON.parse(req.body);
  const lastDocs = await Reviews.find().sort({ id: -1 }).limit(1);
  const new_id   = lastDocs.length ? lastDocs[0].id + 1 : 1;

  const review = new Reviews({
    id: new_id,
    name:          data.name,
    dealership:    data.dealership,
    review:        data.review,
    purchase:      data.purchase,
    purchase_date: data.purchase_date,
    car_make:      data.car_make,
    car_model:     data.car_model,
    car_year:      data.car_year,
  });

  try {
    const saved = await review.save();
    res.json(saved);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Error inserting review' });
  }
});

/* ---------- start server ---------- */
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
