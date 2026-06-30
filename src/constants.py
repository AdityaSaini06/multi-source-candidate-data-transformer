DEFAULT_REGION = "IN" 
DATE_FORMATS_FULL = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d %B %Y", "%B %d, %Y"]
DATE_FORMATS_MONTH_ONLY = ["%Y-%m", "%B %Y", "%b %Y", "%m/%Y"]

SKILL_SYNONYMS = {
    # JavaScript / TypeScript
    "js": "javascript",
    "javascript": "javascript",
    "ecmascript": "javascript",
    "es6": "javascript",
    "es7": "javascript",

    "ts": "typescript",
    "typescript": "typescript",

    # Python
    "py": "python",
    "python": "python",
    "python3": "python",

    # Web
    "html": "html",
    "html5": "html",

    "css": "css",
    "css3": "css",

    "sass": "sass",
    "scss": "sass",
    "less": "less",
    "bootstrap": "bootstrap",
    "tailwind": "tailwind css",
    "tailwindcss": "tailwind css",
    "tailwind css": "tailwind css",

    # C-family
    "c": "c",
    "c99": "c",
    "c11": "c",

    "c++": "c++",
    "cpp": "c++",
    "cxx": "c++",

    "c#": "c#",
    "csharp": "c#",
    ".net": ".net",
    "dotnet": ".net",
    "asp.net": "asp.net",
    "aspnet": "asp.net",

    # Java
    "java": "java",
    "spring": "spring",
    "spring boot": "spring boot",
    "springboot": "spring boot",
    "hibernate": "hibernate",
    "maven": "maven",
    "gradle": "gradle",

    # Frontend
    "react": "react",
    "reactjs": "react",
    "react.js": "react",

    "next": "next.js",
    "nextjs": "next.js",
    "next.js": "next.js",

    "vue": "vue.js",
    "vuejs": "vue.js",
    "vue.js": "vue.js",

    "angular": "angular",
    "angularjs": "angularjs",

    "svelte": "svelte",
    "jquery": "jquery",

    # Backend
    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",

    "express": "express.js",
    "expressjs": "express.js",
    "express.js": "express.js",

    "nestjs": "nestjs",
    "nest": "nestjs",

    "django": "django",
    "flask": "flask",
    "fastapi": "fastapi",

    "laravel": "laravel",
    "php": "php",

    "ruby": "ruby",
    "rails": "ruby on rails",
    "ruby on rails": "ruby on rails",

    "go": "go",
    "golang": "go",

    "rust": "rust",

    "kotlin": "kotlin",

    "swift": "swift",

    "scala": "scala",

    "perl": "perl",

    "r": "r",

    "elixir": "elixir",

    # Mobile
    "android": "android",
    "ios": "ios",

    "react native": "react native",
    "react-native": "react native",

    "flutter": "flutter",
    "dart": "dart",

    "xamarin": "xamarin",

    # Databases
    "sql": "sql",
    "mysql": "mysql",
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "pgsql": "postgresql",

    "sqlite": "sqlite",

    "mssql": "sql server",
    "sql server": "sql server",

    "oracle": "oracle database",

    "mongodb": "mongodb",
    "mongo": "mongodb",

    "redis": "redis",

    "cassandra": "cassandra",

    "firebase": "firebase",

    "supabase": "supabase",

    "dynamodb": "dynamodb",

    "elasticsearch": "elasticsearch",

    # DevOps / Cloud
    "aws": "amazon web services",
    "amazon web services": "amazon web services",

    "azure": "microsoft azure",

    "gcp": "google cloud",
    "google cloud": "google cloud",
    "google cloud platform": "google cloud",

    "docker": "docker",

    "k8s": "kubernetes",
    "kubernetes": "kubernetes",

    "terraform": "terraform",

    "ansible": "ansible",

    "jenkins": "jenkins",

    "github actions": "github actions",

    "gitlab ci": "gitlab ci",

    "circleci": "circleci",

    "nginx": "nginx",

    # Version Control
    "git": "git",
    "github": "github",
    "gitlab": "gitlab",
    "bitbucket": "bitbucket",

    # Data / AI
    "numpy": "numpy",
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "tensorflow": "tensorflow",
    "tf": "tensorflow",
    "keras": "keras",
    "pytorch": "pytorch",
    "torch": "pytorch",
    "opencv": "opencv",

    # APIs
    "rest": "rest api",
    "rest api": "rest api",
    "graphql": "graphql",
    "grpc": "grpc",

    # Testing
    "jest": "jest",
    "mocha": "mocha",
    "chai": "chai",
    "cypress": "cypress",
    "playwright": "playwright",
    "selenium": "selenium",

    # Misc
    "linux": "linux",
    "bash": "bash",
    "shell": "shell scripting",
    "shell scripting": "shell scripting",
}

COUNTRY_NAME_TO_ALPHA2 = {
    # Asia
    "india": "IN",
    "china": "CN",
    "japan": "JP",
    "south korea": "KR",
    "korea": "KR",
    "north korea": "KP",
    "singapore": "SG",
    "malaysia": "MY",
    "indonesia": "ID",
    "thailand": "TH",
    "vietnam": "VN",
    "philippines": "PH",
    "pakistan": "PK",
    "bangladesh": "BD",
    "nepal": "NP",
    "sri lanka": "LK",
    "bhutan": "BT",
    "maldives": "MV",
    "afghanistan": "AF",
    "iran": "IR",
    "iraq": "IQ",
    "israel": "IL",
    "saudi arabia": "SA",
    "uae": "AE",
    "united arab emirates": "AE",
    "qatar": "QA",
    "kuwait": "KW",
    "oman": "OM",
    "bahrain": "BH",
    "turkey": "TR",

    # Europe
    "united kingdom": "GB",
    "uk": "GB",
    "great britain": "GB",
    "england": "GB",
    "scotland": "GB",
    "wales": "GB",

    "ireland": "IE",
    "france": "FR",
    "germany": "DE",
    "italy": "IT",
    "spain": "ES",
    "portugal": "PT",
    "netherlands": "NL",
    "belgium": "BE",
    "switzerland": "CH",
    "austria": "AT",
    "sweden": "SE",
    "norway": "NO",
    "denmark": "DK",
    "finland": "FI",
    "poland": "PL",
    "czech republic": "CZ",
    "czechia": "CZ",
    "hungary": "HU",
    "romania": "RO",
    "greece": "GR",
    "ukraine": "UA",
    "russia": "RU",

    # North America
    "united states": "US",
    "usa": "US",
    "u.s.a.": "US",
    "united states of america": "US",
    "america": "US",
    "canada": "CA",
    "mexico": "MX",

    # South America
    "brazil": "BR",
    "argentina": "AR",
    "chile": "CL",
    "colombia": "CO",
    "peru": "PE",
    "uruguay": "UY",
    "paraguay": "PY",
    "ecuador": "EC",
    "venezuela": "VE",
    "bolivia": "BO",

    # Africa
    "south africa": "ZA",
    "egypt": "EG",
    "nigeria": "NG",
    "kenya": "KE",
    "ethiopia": "ET",
    "ghana": "GH",
    "morocco": "MA",
    "tunisia": "TN",
    "algeria": "DZ",

    # Oceania
    "australia": "AU",
    "new zealand": "NZ",
    "fiji": "FJ",
    "papua new guinea": "PG",
}