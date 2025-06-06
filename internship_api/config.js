require('dotenv').config();

module.exports = {
  APP_ID: process.env.ADZUNA_APP_ID,
  API_KEY: process.env.ADZUNA_APP_KEY,
  BASE_URL: 'https://api.adzuna.com/v1/api/jobs',
  BASE_PARAMS: 'search/1?results_per_page=20&content-type=application/json',
};
