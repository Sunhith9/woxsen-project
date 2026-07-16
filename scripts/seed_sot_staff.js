// SOT Staff Seed Script
// Run in browser console or Node.js (with node-fetch)
// 1. Deletes all existing SOT (School of Technology) staff from staff_accounts
// 2. Inserts 44 SOT faculty members from the provided list

const SB_URL = 'https://ohmeixzrfbyccmymzgjp.supabase.co/rest/v1';
const SB_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9obWVpeHpyZmJ5Y2NteW16Z2pwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE3NjgwNDYsImV4cCI6MjA4NzM0NDA0Nn0.QZJYRXYoZxeTTvkKFC6JzQ8Jykbf-RYVUdJwfnEaPxc';

const HEADERS = {
    'Content-Type': 'application/json',
    'apikey': SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
    'Prefer': 'return=representation'
};

const SOT_STAFF = [
    { fullname: 'Dr. Rajesh Kumar K V',              role: 'Associate Dean',                          email: 'rajesh.kumar@woxsen.edu.in',              phone: '9985622799', emp_id: '170362' },
    { fullname: 'Dr. Amogh Deshmukh',                role: 'Assistant Dean- Student Affairs',          email: 'amogh.deshmukh@woxsen.edu.in',            phone: '9000569938', emp_id: '170333' },
    { fullname: 'Dr. Sarah Mariam Roy',              role: 'Assistant Dean- Organizational Alignment', email: 'sarah.mariam@woxsen.edu.in',              phone: '9446975177', emp_id: '170824' },
    { fullname: 'Dr. Monday Jubrin Abdullahi',       role: 'Assistant Professor',                     email: 'abdullahi.monday@woxsen.edu.in',           phone: '7075173128', emp_id: '171340' },
    { fullname: 'Dr. Bhargav Pragwal Pathri',        role: 'Associate Professor',                     email: 'bhargav.pathri@woxsen.edu.in',             phone: '7227933987', emp_id: '170440' },
    { fullname: 'Dr. S. Bhanu Prakash',              role: 'Associate Professor',                     email: 'bhanu.prakash@woxsen.edu.in',              phone: '9985944770', emp_id: '170536' },
    { fullname: 'Dr. Ibitoye Segun Emmanuel',        role: 'Assistant Professor',                     email: 'ibitoye.emmanuel@woxsen.edu.in',           phone: '',           emp_id: '171311' },
    { fullname: 'Prof. Meher Gayatri Davi',          role: 'Assistant Professor',                     email: 'mehergayatri.tiwari@woxsen.edu.in',        phone: '9003147555', emp_id: '171295' },
    { fullname: 'Dr. Syed Javeed',                   role: 'Assistant Professor',                     email: 'syedjaveed.pasha@woxsen.edu.in',           phone: '8555092262', emp_id: '170899' },
    { fullname: 'Dr. Roopa Vuppula',                 role: 'Assistant Professor',                     email: 'roopa.vuppula@woxsen.edu.in',              phone: '8919236916', emp_id: '171406' },
    { fullname: 'Dr. Dharmendra Kr Mishra',          role: 'Assistant Professor',                     email: 'dharamendra.mishra@woxsen.edu.in',         phone: '6396928590', emp_id: '170941' },
    { fullname: 'Dr. T Santhosh Kumar',              role: 'Assistant Professor',                     email: 'santhosh.kumar@woxsen.edu.in',             phone: '9955706093', emp_id: '170999' },
    { fullname: 'Dr. Venakata Narayana',             role: 'Assistant Professor',                     email: 'venkata.narayana@woxsen.edu.in',           phone: '8264314474', emp_id: '170499' },
    { fullname: 'Dr. T Ravinder',                    role: 'Associate Professor',                     email: 'tadi.ravindar@woxsen.edu.in',              phone: '9705713477', emp_id: '171287' },
    { fullname: 'Dr. Kamil Reza',                    role: 'Assistant Professor',                     email: 'kamil.reza@woxsen.edu.in',                phone: '9891979373', emp_id: '170908' },
    { fullname: 'Dr. Ram Soorat',                    role: 'Assistant Professor',                     email: 'ram.soorat@woxsen.edu.in',                phone: '9985890110', emp_id: '170847' },
    { fullname: 'Dr. Ravi Kiran Kummamuru',          role: 'Professor',                               email: 'ravikiran.Kummamuru@woxsen.edu.in',        phone: '7893498684', emp_id: '171520' },
    { fullname: 'Dr. Rajkumar Kalimuthu',            role: 'Associate Professor',                     email: 'rajkumar.kalimuthu@woxsen.edu.in',         phone: '7339061677', emp_id: '171524' },
    { fullname: 'Dr. Malli Rajeswara Rao',           role: 'Assistant Professor',                     email: 'rajeswara.rao@woxsen.edu.in',              phone: '7702966206', emp_id: '171526' },
    { fullname: 'Dr. Lokendra Gour',                 role: 'Assistant Professor',                     email: 'lokendra.gour@woxsen.edu.in',              phone: '7879309911', emp_id: '171523' },
    { fullname: 'Dr. Karthick N',                    role: 'Assistant Professor',                     email: 'karthick.n@woxsen.edu.in',                phone: '9003807075', emp_id: '171525' },
    { fullname: 'Dr. Anusree',                       role: 'Assistant Professor',                     email: 'anusree.b@woxsen.edu.in',                 phone: '7306474785', emp_id: '171574' },
    { fullname: 'Dr. Udhay Bhaskar',                 role: 'Assistant Professor',                     email: 'udayabhaskar.pattapu@woxsen.edu.in',       phone: '7033695847', emp_id: '171572' },
    { fullname: 'Dr. Gurunath Sahu',                 role: 'Assistant Professor',                     email: 'gurunath.sahu@woxsen.edu.in',              phone: '9583907544', emp_id: '171579' },
    { fullname: 'Dr. P B Sharon',                    role: 'Assistant Professor',                     email: 'sharon.pb@woxsen.edu.in',                 phone: '8086992029', emp_id: '171582' },
    { fullname: 'Dr. Soujanya',                      role: 'Assistant Professor',                     email: 'soujanya.n@woxsen.edu.in',                phone: '9989813822', emp_id: '171590' },
    { fullname: 'Dr. Uday Chandra A',                role: 'Assistant Professor',                     email: 'uday.chandra@woxsen.edu.in',               phone: '8309668912', emp_id: '171597' },
    { fullname: 'Dr. Nagaraju Dharavat',             role: 'Associate Professor',                     email: 'nagaraju.dharavat@woxsen.edu.in',          phone: '8096846252', emp_id: '171592' },
    { fullname: 'Dr. B Sanjai Prasada Rao',          role: 'Associate Professor',                     email: 'sanjaiprasad.rao@woxsen.edu.in',           phone: '9492883373', emp_id: '171607' },
    { fullname: 'Prof. Geeta Tripathi',              role: 'Professor of Practice',                   email: 'geeta.tripathi@woxsen.edu.in',             phone: '9910906776', emp_id: '171620' },
    { fullname: 'Prof. Veeresh Biradar',             role: 'Assistant Professor',                     email: 'veeresh.biradar@woxsen.edu.in',            phone: '9620655847', emp_id: '171636' },
    { fullname: 'Prof. Gururaj Nase',                role: 'Assistant Professor',                     email: 'gururaj.nase@woxsen.edu.in',               phone: '9449460181', emp_id: '171635' },
    { fullname: 'Dr. Muralidhar Goud K',             role: 'Assistant Professor',                     email: 'muralidhar.k@woxsen.edu.in',               phone: '6301667259', emp_id: '171698' },
    { fullname: 'Prof. Mulkala Saritha',             role: 'Assistant Professor',                     email: 'saritha.mulkala@woxsen.edu.in',            phone: '8121828543', emp_id: '171711' },
    { fullname: 'Dr. M Shiva Rama Krishna',          role: 'Assistant Professor',                     email: 'shivarama.mallu@woxsen.edu.in',            phone: '8328225191', emp_id: '171713' },
    { fullname: 'Prof. Rupinder Saini',              role: 'Assistant Professor',                     email: 'rupinder.saini@woxsen.edu.in',             phone: '8360605698', emp_id: '171708' },
    { fullname: 'Dr. Somnath Karmakar',              role: 'Assistant Professor',                     email: 'somnath.karmakar@woxsen.edu.in',           phone: '9434536394', emp_id: '171703' },
    { fullname: 'Dr. Sarasija Das',                  role: 'Assistant Professor',                     email: 'sarasija.das@woxsen.edu.in',               phone: '9064012558', emp_id: '171701' },
    { fullname: 'Prof. Dileep Kumar Mahadevabatla',  role: 'Professor of Practice',                   email: 'dileep.mahadevabatla@woxsen.edu.in',       phone: '9705607612', emp_id: '171715' },
    { fullname: 'Prof. Sahithi',                     role: 'Assistant Professor',                     email: 'sahithi.chennamadhavuni@woxsen.edu.in',    phone: '9959135015', emp_id: '171722' },
    { fullname: 'Dr. Haritha R',                     role: 'Assistant Professor',                     email: 'haritha.r@woxsen.edu.in',                 phone: '8985244921', emp_id: '171724' },
    { fullname: 'Dr. YVR Naga Pawan',                role: 'Associate Professor',                     email: 'nagapawan.y@woxsen.edu.in',                phone: '9704567458', emp_id: '171734' },
    { fullname: 'Dr. Upendra Kumar',                 role: 'Professor',                               email: 'upendra.kumar@woxsen.edu.in',              phone: '9885253205', emp_id: '171735' },
    { fullname: 'Dr. Kiran Mayee Adavala',           role: 'Professor',                               email: 'kiranmayee.a@woxsen.edu.in',               phone: '9290200204', emp_id: '171736' },
];

async function sbFetch(path, opts = {}) {
    const h = { ...HEADERS };
    if (opts.prefer) h['Prefer'] = opts.prefer;
    const fetchOpts = { method: opts.method || 'GET', headers: h };
    if (opts.body) fetchOpts.body = opts.body;
    return fetch(SB_URL + '/' + path, fetchOpts);
}

async function seedSOT() {
    console.log('=== SOT Staff Seed Script ===');

    // STEP 1: Fetch existing SOT academic staff
    console.log('\n[1/3] Fetching existing SOT Academic staff...');
    const fetchResp = await sbFetch('staff_accounts?dept=eq.Academic&select=id,fullname,sub_dept');
    if (!fetchResp.ok) { console.error('Failed to fetch:', await fetchResp.text()); return; }
    const existing = await fetchResp.json();
    const sotExisting = existing.filter(s => (s.sub_dept || '').includes('School of Technology'));
    console.log(`Found ${sotExisting.length} existing SOT staff.`);

    // STEP 2: Delete them
    if (sotExisting.length > 0) {
        console.log('\n[2/3] Deleting existing SOT staff...');
        for (const s of sotExisting) {
            const del = await sbFetch('staff_accounts?id=eq.' + s.id, { method: 'DELETE' });
            console.log(del.ok ? `  Deleted: ${s.fullname}` : `  Failed: ${s.fullname}`);
        }
    } else {
        console.log('\n[2/3] No existing SOT staff — skipping delete.');
    }

    // STEP 3: Insert 44 new SOT staff
    console.log('\n[3/3] Inserting 44 SOT faculty...');
    let ok = 0, fail = 0;
    for (const f of SOT_STAFF) {
        const obj = {
            fullname: f.fullname,
            role: f.role,
            dept: 'Academic',
            email: f.email,
            phone: f.phone,
            username: f.emp_id,
            password: f.emp_id,
            sub_dept: 'School of Technology',
            status: 'Active',
            joined: ''
        };
        const r = await sbFetch('staff_accounts', {
            method: 'POST',
            prefer: 'return=representation',
            body: JSON.stringify(obj)
        });
        if (r.ok) { ok++; console.log(`  ✓ ${f.fullname}`); }
        else { fail++; console.error(`  ✗ ${f.fullname}:`, await r.text()); }
    }
    console.log(`\n=== Done: ${ok} inserted, ${fail} failed. ===`);
}

seedSOT();
