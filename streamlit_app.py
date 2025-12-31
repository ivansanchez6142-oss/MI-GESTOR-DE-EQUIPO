import React, { useState, useEffect } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInWithCustomToken, signInAnonymously, onAuthStateChanged } from 'firebase/auth';
import {
  getFirestore,
  doc,
  collection,
  onSnapshot,
  addDoc,
  setDoc,
  deleteDoc,
  query,
  where,
  orderBy,
  serverTimestamp,
} from 'firebase/firestore';

// Moved ScoutingDetailInput outside the App component to prevent re-creation on re-renders.
// This fixes the issue where the textarea loses focus after typing a single character.
const ScoutingDetailInput = ({ category, field, placeholder, value, handleNestedChange }) => (
  <textarea
    value={value}
    onChange={(e) => handleNestedChange(category, field, e.target.value)}
    placeholder={placeholder}
    className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
    rows="2"
  ></textarea>
);

// Main application component
const App = () => {
  // State variables for teams and seasons
  const [teams, setTeams] = useState([]);
  const [seasons, setSeasons] = useState([]);
  const [selectedTeamId, setSelectedTeamId] = useState('');
  const [selectedSeasonId, setSelectedSeasonId] = useState('');
  const [newTeamName, setNewTeamName] = useState('');
  const [newSeasonName, setNewSeasonName] = useState('');
  const [editingTeam, setEditingTeam] = useState(null);
  const [editingSeason, setEditingSeason] = useState(null);

  // State variables for team members
  const [teamMembers, setTeamMembers] = useState([]);
  const [newMemberFullName, setNewMemberFullName] = useState('');
  const [newMemberDateOfBirth, setNewMemberDateOfBirth] = useState('');
  const [newMemberPosition, setNewMemberPosition] = useState('');
  const [newMemberSecondaryPosition, setNewMemberSecondaryPosition] = useState('');
  const [newMemberDominantLeg, setNewMemberDominantLeg] = useState('');
  const [newMemberWeight, setNewMemberWeight] = useState('');
  const [newMemberHeight, setNewMemberHeight] = useState('');
  const [editingMemberId, setEditingMemberId] = useState(null);
  const [editingFullName, setEditingFullName] = useState('');
  const [editingDateOfBirth, setEditingDateOfBirth] = useState('');
  const [editingPosition, setEditingPosition] = useState('');
  const [editingSecondaryPosition, setEditingSecondaryPosition] = useState('');
  const [editingDominantLeg, setEditingDominantLeg] = useState('');
  const [editingWeight, setEditingWeight] = useState('');
  const [editingHeight, setEditingHeight] = useState('');
  const [viewingMember, setViewingMember] = useState(null); // State for viewing member details

  // State variables for training sessions
  const [trainingSessions, setTrainingSessions] = useState([]);
  const [newTraining, setNewTraining] = useState({
    date: '', time: '', place: '', macrociclo: '', mesociclo: '', microciclo: '', session: '', objectives: '', category: '',
    warmup: { description: '', rules: '', coachMessage: '', duration: '', series: '', rest: '', space: '' },
    analyticExercise: { description: '', rules: '', coachMessage: '', duration: '', series: '', rest: '', space: '' },
    introductoryExercise: { description: '', rules: '', coachMessage: '', duration: '', series: '', rest: '', space: '' },
    tacticalExercise: { description: '', rules: '', coachMessage: '', duration: '', series: '', rest: '', space: '' },
    ABP: { description: '', rules: '', coachMessage: '', duration: '', series: '', rest: '' },
    cooldown: { description: '', rules: '', coachMessage: '', duration: '', series: '', rest: '' },
    coachesRoles: '', totalVolume: '', photoLinks: '', videoLinks: '', tacticalPrinciples: []
  });
  const [editingTrainingId, setEditingTrainingId] = useState(null);
  const [viewingTraining, setViewingTraining] = useState(null); // State for viewing training details

  // State variables for attendance tracking
  const [attendance, setAttendance] = useState({});

  // State variables for tactical principles
  const [tacticalPrinciples, setTacticalPrinciples] = useState([]);
  const [newPrincipleName, setNewPrincipleName] = useState('');
  const [editingPrincipleId, setEditingPrincipleId] = useState(null);
  const [editingPrincipleName, setEditingPrincipleName] = useState('');
  const [principleExplanation, setPrincipleExplanation] = useState('');
  const [isExplainingPrinciple, setIsExplainingPrinciple] = useState(false);

  // State variables for Gemini AI integration
  const [generationObjectives, setGenerationObjectives] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState(null);

  // State variables for match plans
  const [matchPlans, setMatchPlans] = useState([]);
  const [newMatchPlan, setNewMatchPlan] = useState({
    rival: '',
    date: '',
    place: '',
    time: '',
    rivalStrengths: '',
    rivalWeaknesses: '',
    offensiveOrganization: '',
    defensiveOrganization: '',
    offensiveTransition: '',
    defensiveTransition: '',
    offensiveABP: '',
    defensiveABP: '',
    additionalNotes: '',
    videoLink: ''
  });
  const [editingMatchPlanId, setEditingMatchPlanId] = useState(null);

  // UI state for navigation
  const [currentSection, setCurrentSection] = useState('gestion');

  // State variables for training videos
  const [activeVideoSection, setActiveVideoSection] = useState('mis_entrenamientos');
  const [myTrainings, setMyTrainings] = useState({});
  const [otherTrainings, setOtherTrainings] = useState({});
  const [newVideo, setNewVideo] = useState({ name: '', url: '', category: '' });
  const [editingVideo, setEditingVideo] = useState(null);
  
  // State variables for Video Analysis
  const initialAnalysisState = {
    equipoAnalizado: '', rival: '', lugar: '', fechaInforme: '',
    sistemaJuego: '',
    organizacionOfensiva: { inicio: '', creacion: '', finalizacion: '' },
    organizacionDefensiva: '',
    transicionOfensiva: '',
    transicionDefensiva: '',
    abpOfensivo: '',
    abpDefensivo: '',
    laterales: '',
    fortalezas: '',
    debilidades: '',
    notasAdicionales: '',
    enlaceVideo: ''
  };
  const [videoAnalyses, setVideoAnalyses] = useState({ myTeam: [], rivalTeam: [] });
  const [activeAnalysisSection, setActiveAnalysisSection] = useState('myTeam');
  const [newAnalysis, setNewAnalysis] = useState(initialAnalysisState);
  const [editingAnalysisId, setEditingAnalysisId] = useState(null);
  const [viewingAnalysis, setViewingAnalysis] = useState(null);
  
  // State variables for Matches
  const initialMatchState = {
    rival: '', fecha: '', lugar: '', hora: '', resultado: '', sistemaUtilizado: '', titulares: '', suplentes: '',
    observaciones: { organizacionOfensiva: '', organizacionDefensiva: '', transicionOfensiva: '', transicionDefensiva: '', abpOfensivo: '', abpDefensivo: '', notasAdicionales: '' },
    enlaceVideo: '',
    events: []
  };
  const [matches, setMatches] = useState([]);
  const [newMatch, setNewMatch] = useState(initialMatchState);
  const [editingMatchId, setEditingMatchId] = useState(null);
  const [viewingMatch, setViewingMatch] = useState(null);
  const [newEvent, setNewEvent] = useState({ player: '', type: '', detail: '' });
  
  // State variables for Scouting
  const initialScoutingState = {
    nombreJugador: '', fechaNacimiento: '', edad: '', categoria: '', club: '',
    posicionPrincipal: '', posicionSecundaria: '', piernaHabil: '', talla: '', peso: '',
    fechaInforme: '',
    fortalezas: { tecnica: '', tacticaIndividual: '', tacticaColectivaOfensiva: '', tacticaColectivaDefensiva: '', juegoAereo: '', comunicacion: '', actitudes: '', fisico: '', tiroLibres: '', penales: '' },
    debilidades: { tecnica: '', tacticaIndividual: '', tacticaColectivaOfensiva: '', tacticaColectivaDefensiva: '', juegoAereo: '', comunicacion: '', actitudes: '', fisico: '', tiroLibres: '', penales: '' },
    historialLesiones: '',
    notasAdicionales: '', enlaceVideo: ''
  };
  const [scoutingReports, setScoutingReports] = useState([]);
  const [newScoutingReport, setNewScoutingReport] = useState(initialScoutingState);
  const [editingScoutingReportId, setEditingScoutingReportId] = useState(null);
  const [viewingScoutingReport, setViewingScoutingReport] = useState(null);

  // State variables for Player Stats
  const [playerStats, setPlayerStats] = useState({});

  // State variables for Match Videos
  const [matchVideos, setMatchVideos] = useState({ myTeamMatches: [], rivalTeamMatches: [], others: [] });
  const [activeMatchVideoSection, setActiveMatchVideoSection] = useState('myTeamMatches');
  const [newMatchVideo, setNewMatchVideo] = useState({ teams: '', link: '' });
  const [editingMatchVideo, setEditingMatchVideo] = useState(null);

  // Firestore and Auth state
  const [db, setDb] = useState(null);
  const [auth, setAuth] = useState(null);
  const [userId, setUserId] = useState(null);
  const [isAuthReady, setIsAuthReady] = useState(false);
  const [isLoadingVideos, setIsLoadingVideos] = useState(true);
  const [videoMessage, setVideoMessage] = useState(null);

  // Predefined options
  const positions = ["Arquero", "Defensor Central", "Lateral", "Volante Central", "Volante Interno", "Volante Externo", "Media Punta", "Extremo", "Centro Delantero"];
  const dominantLegs = ["Derecha", "Izquierda", "Ambas"];
  const justifications = ["Lesión", "Enfermedad", "Viaje", "Estudio", "Sin justificar"];
  const categories = [
    'Inicio de ataque organizado',
    'Creación y progresión',
    'Finalización',
    'Transición ofensiva',
    'Transición defensiva',
    'ABP Ofensivo',
    'ABP defensivo',
    'Laterales'
  ];
  const eventTypes = [
    { value: 'gol', label: 'Gol' },
    { value: 'gol_cabeza', label: 'Gol de Cabeza' },
    { value: 'gol_tiro_libre', label: 'Gol de Tiro Libre' },
    { value: 'gol_penal', label: 'Gol de Penal' },
    { value: 'asistencia', label: 'Asistencia' },
    { value: 'tarjeta_amarilla', label: 'Tarjeta Amarilla' },
    { value: 'tarjeta_roja', label: 'Tarjeta Roja' },
    { value: 'lesion', label: 'Lesión' },
  ];

  // Helper function to get today's date in YYYY-MM-DD format
  const getTodayDate = () => {
    const date = new Date();
    return date.getFullYear() + '-' + ('0' + (date.getMonth() + 1)).slice(-2) + '-' + ('0' + date.getDate()).slice(-2);
  };
  const todayDate = getTodayDate();

  // Helper function to format minutes into hours and minutes
  const formatMinutes = (totalMinutes) => {
    const hours = Math.floor(totalMinutes / 60);
    const minutes = totalMinutes % 60;
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  // Dynamically load scripts for exporting
  useEffect(() => {
    const loadScript = (src, id) => {
        if (document.getElementById(id)) return;
        const script = document.createElement('script');
        script.src = src;
        script.id = id;
        script.async = true;
        document.body.appendChild(script);
    };

    loadScript('https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js', 'xlsx-script');
    loadScript('https://unpkg.com/docx@7.3.0/build/index.js', 'docx-script');
  }, []);

  // Firebase configuration and authentication
  useEffect(() => {
    const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
    const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : {};
    const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;

    try {
      const app = initializeApp(firebaseConfig);
      const firestoreDb = getFirestore(app);
      const firebaseAuth = getAuth(app);
      setDb(firestoreDb);
      setAuth(firebaseAuth);

      onAuthStateChanged(firebaseAuth, async (user) => {
        if (user) {
          setUserId(user.uid);
        } else {
          try {
            if (initialAuthToken) {
              await signInWithCustomToken(firebaseAuth, initialAuthToken);
            } else {
              await signInAnonymously(firebaseAuth);
            }
          } catch (error) {
            console.error('Error signing in:', error);
          }
        }
        setIsAuthReady(true);
      });

    } catch (error) {
      console.error("Firebase initialization failed:", error);
    }
  }, []);

  // Firestore listeners for teams, seasons, members, trainings, and attendance
  useEffect(() => {
    if (!userId || !db) return; // Wait for authentication and DB initialization

    const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';

    // Listener for teams
    const teamsRef = collection(db, `artifacts/${appId}/public/data/teams`);
    const teamsQuery = query(teamsRef, orderBy('createdAt'));
    const unsubscribeTeams = onSnapshot(teamsQuery, (snapshot) => {
      const teamsData = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setTeams(teamsData);
      if (!selectedTeamId && teamsData.length > 0) {
        setSelectedTeamId(teamsData[0].id);
      }
    }, (error) => console.error('Error listening to teams:', error));

    // Listener for seasons
    let unsubscribeSeasons = () => {};
    if (selectedTeamId) {
      const seasonsRef = collection(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons`);
      const seasonsQuery = query(seasonsRef, orderBy('createdAt'));
      unsubscribeSeasons = onSnapshot(seasonsQuery, (snapshot) => {
        const seasonsData = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        setSeasons(seasonsData);
        if (!selectedSeasonId && seasonsData.length > 0) {
          setSelectedSeasonId(seasonsData[0].id);
        }
      }, (error) => console.error('Error listening to seasons:', error));
    }

    // Listeners for data within a season
    let unsubscribeAllSeasonData = () => {};
    if (selectedTeamId && selectedSeasonId) {
      const membersRef = collection(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/teamMembers`);
      const membersQuery = query(membersRef, orderBy('createdAt'));
      const unsubscribeMembers = onSnapshot(membersQuery, (snapshot) => {
        setTeamMembers(snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })));
      }, (error) => console.error('Error listening to members:', error));

      const trainingsRef = collection(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/trainings`);
      const trainingsQuery = query(trainingsRef, orderBy('date'));
      const unsubscribeTrainings = onSnapshot(trainingsQuery, (snapshot) => {
        setTrainingSessions(snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })));
      }, (error) => console.error('Error listening to trainings:', error));

      const attendanceRef = doc(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/attendance/${todayDate}`);
      const unsubscribeAttendance = onSnapshot(attendanceRef, (docSnapshot) => {
        setAttendance(docSnapshot.exists() ? docSnapshot.data() : {});
      }, (error) => console.error('Error listening to attendance:', error));

      const principlesRef = collection(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/tacticalPrinciples`);
      const principlesQuery = query(principlesRef, orderBy('name'));
      const unsubscribePrinciples = onSnapshot(principlesQuery, (snapshot) => {
        setTacticalPrinciples(snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })));
      }, (error) => console.error('Error listening to principles:', error));

      const matchPlansRef = collection(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/matchPlans`);
      const matchPlansQuery = query(matchPlansRef, orderBy('date'));
      const unsubscribeMatchPlans = onSnapshot(matchPlansQuery, (snapshot) => {
        setMatchPlans(snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })));
      }, (error) => console.error('Error listening to match plans:', error));
      
      const analysisRef = collection(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/videoAnalysis`);
      const unsubscribeAnalysis = onSnapshot(analysisRef, (snapshot) => {
        const allAnalyses = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        setVideoAnalyses({
          myTeam: allAnalyses.filter(a => a.type === 'myTeam'),
          rivalTeam: allAnalyses.filter(a => a.type === 'rivalTeam'),
        });
      }, (error) => console.error('Error listening to video analysis:', error));

      const matchesRef = collection(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/matches`);
      const unsubscribeMatches = onSnapshot(matchesRef, (snapshot) => {
        setMatches(snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })));
      }, (error) => console.error('Error listening to matches:', error));
      
      const scoutingRef = collection(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/scoutingReports`);
      const unsubscribeScouting = onSnapshot(scoutingRef, (snapshot) => {
        setScoutingReports(snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })));
      }, (error) => console.error('Error listening to scouting reports:', error));

      const matchVideosRef = collection(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/matchVideos`);
      const unsubscribeMatchVideos = onSnapshot(matchVideosRef, (snapshot) => {
        const allVideos = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        setMatchVideos({
          myTeamMatches: allVideos.filter(v => v.type === 'myTeamMatches'),
          rivalTeamMatches: allVideos.filter(v => v.type === 'rivalTeamMatches'),
          others: allVideos.filter(v => v.type === 'others'),
        });
      }, (error) => console.error('Error listening to match videos:', error));

      unsubscribeAllSeasonData = () => {
        unsubscribeMembers();
        unsubscribeTrainings();
        unsubscribeAttendance();
        unsubscribePrinciples();
        unsubscribeMatchPlans();
        unsubscribeAnalysis();
        unsubscribeMatches();
        unsubscribeScouting();
        unsubscribeMatchVideos();
      };
    }

    return () => {
      unsubscribeTeams();
      unsubscribeSeasons();
      unsubscribeAllSeasonData();
    };
  }, [db, userId, selectedTeamId, selectedSeasonId, todayDate]);


  // Firestore listeners for training videos
  useEffect(() => {
    if (!userId || !db) {
      setIsLoadingVideos(false);
      return;
    }
    setIsLoadingVideos(true);
    const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';

    const myTrainingsCollectionPath = `artifacts/${appId}/users/${userId}/mis_entrenamientos`;
    const otherTrainingsCollectionPath = `artifacts/${appId}/public/data/otros_entrenamientos`;

    const myTrainingsQuery = query(collection(db, myTrainingsCollectionPath));
    const otherTrainingsQuery = query(collection(db, otherTrainingsCollectionPath));

    const unsubscribeMyTrainings = onSnapshot(myTrainingsQuery, (snapshot) => {
        const data = {};
        snapshot.docs.forEach(doc => {
            const video = { id: doc.id, ...doc.data() };
            const category = video.category;
            if (!data[category]) {
                data[category] = [];
            }
            data[category].push(video);
        });
        setMyTrainings(data);
        setIsLoadingVideos(false);
    }, (error) => {
        console.error('Error fetching my trainings:', error);
        setVideoMessage('Error al cargar "Mis Entrenamientos".');
        setIsLoadingVideos(false);
    });

    const unsubscribeOtherTrainings = onSnapshot(otherTrainingsQuery, (snapshot) => {
        const data = {};
        snapshot.docs.forEach(doc => {
            const video = { id: doc.id, ...doc.data() };
            const category = video.category;
            if (!data[category]) {
                data[category] = [];
            }
            data[category].push(video);
        });
        setOtherTrainings(data);
        setIsLoadingVideos(false);
    }, (error) => {
        console.error('Error fetching other trainings:', error);
        setVideoMessage('Error al cargar "Entrenamientos de otros entrenadores".');
        setIsLoadingVideos(false);
    });

    return () => {
        unsubscribeMyTrainings();
        unsubscribeOtherTrainings();
    };
  }, [db, userId]);

  // Calculate player statistics from matches
  useEffect(() => {
    const stats = {};
    teamMembers.forEach(member => {
      stats[member.fullName] = {
        titular: 0, minutosJugados: 0, goles: 0, golesDeCabeza: 0, golesDeTiroLibre: 0,
        golesDePenal: 0, asistencias: 0, tarjetasAmarillas: 0, tarjetasRojas: 0, lesiones: []
      };
    });

    matches.forEach(match => {
      // Calculate minutes from starters
      teamMembers.forEach(member => {
        if (match.titulares && match.titulares.includes(member.fullName)) {
          stats[member.fullName].titular += 1;
          stats[member.fullName].minutosJugados += 90; // Simplified for now
        }
      });

      // Process events
      if (match.events) {
        match.events.forEach(event => {
          if (stats[event.player]) {
            switch (event.type) {
              case 'gol':
                stats[event.player].goles += 1;
                break;
              case 'gol_cabeza':
                stats[event.player].goles += 1;
                stats[event.player].golesDeCabeza += 1;
                break;
              case 'gol_tiro_libre':
                stats[event.player].goles += 1;
                stats[event.player].golesDeTiroLibre += 1;
                break;
              case 'gol_penal':
                stats[event.player].goles += 1;
                stats[event.player].golesDePenal += 1;
                break;
              case 'asistencia':
                stats[event.player].asistencias += 1;
                break;
              case 'tarjeta_amarilla':
                stats[event.player].tarjetasAmarillas += 1;
                break;
              case 'tarjeta_roja':
                stats[event.player].tarjetasRojas += 1;
                break;
              case 'lesion':
                stats[event.player].lesiones.push(event.detail || 'Lesión no especificada');
                break;
              default:
                break;
            }
          }
        });
      }
    });
    setPlayerStats(stats);
  }, [matches, teamMembers]);

  // Generic Export Functions
  const exportToExcel = (data, fileName) => {
    if (typeof XLSX === 'undefined') {
        alert('La librería para exportar a Excel no está cargada. Por favor, espera un momento y vuelve a intentarlo.');
        return;
    }
    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Datos');
    XLSX.writeFile(wb, `${fileName}.xlsx`);
  };

  const exportToWord = (doc, fileName) => {
    if (typeof docx === 'undefined') {
        alert('La librería para exportar a Word no está cargada. Por favor, espera un momento y vuelve a intentarlo.');
        return;
    }
    docx.Packer.toBlob(doc).then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${fileName}.docx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    });
  };

  // Gemini API call for generating training sessions
  const generateTrainingWithGemini = async () => {
    if (!generationObjectives.trim()) {
      setGenerationError('Por favor, ingresa los objetivos del entrenamiento.');
      return;
    }

    setIsGenerating(true);
    setGenerationError(null);

    const prompt = `Genera una sesión de entrenamiento de fútbol completa basada en los siguientes objetivos: "${generationObjectives}". La respuesta debe ser un objeto JSON que incluya:
- objectives: una string con los objetivos de la sesión.
- warmup: un objeto para el calentamiento con "description", "rules", "coachMessage", "duration", "series", "rest", y "space".
- analyticExercise: un objeto para el ejercicio analítico con las mismas propiedades.
- introductoryExercise: un objeto para el ejercicio introductorio con las mismas propiedades.
- tacticalExercise: un objeto para el ejercicio táctico con las mismas propiedades.
- tacticalPrinciples: un array de objetos, donde cada objeto tiene "name" y "duration". Selecciona principios tácticos relevantes de la siguiente lista: ${tacticalPrinciples.map(p => p.name).join(', ')}.

Asegúrate de que la descripción sea detallada y las reglas sean claras. El JSON debe ser válido y no contener ningún otro texto fuera de él.`;

    const payload = {
      contents: [{ role: 'user', parts: [{ text: prompt }] }],
      generationConfig: {
        responseMimeType: "application/json",
        responseSchema: {
          "type": "OBJECT",
          "properties": {
            "objectives": { "type": "STRING" },
            "warmup": {
              "type": "OBJECT",
              "properties": {
                "description": { "type": "STRING" },
                "rules": { "type": "STRING" },
                "coachMessage": { "type": "STRING" },
                "duration": { "type": "NUMBER" },
                "series": { "type": "NUMBER" },
                "rest": { "type": "NUMBER" },
                "space": { "type": "STRING" }
              }
            },
            "analyticExercise": {
              "type": "OBJECT",
              "properties": {
                "description": { "type": "STRING" },
                "rules": { "type": "STRING" },
                "coachMessage": { "type": "STRING" },
                "duration": { "type": "NUMBER" },
                "series": { "type": "NUMBER" },
                "rest": { "type": "NUMBER" },
                "space": { "type": "STRING" }
              }
            },
            "introductoryExercise": {
              "type": "OBJECT",
              "properties": {
                "description": { "type": "STRING" },
                "rules": { "type": "STRING" },
                "coachMessage": { "type": "STRING" },
                "duration": { "type": "NUMBER" },
                "series": { "type": "NUMBER" },
                "rest": { "type": "NUMBER" },
                "space": { "type": "STRING" }
              }
            },
            "tacticalExercise": {
              "type": "OBJECT",
              "properties": {
                "description": { "type": "STRING" },
                "rules": { "type": "STRING" },
                "coachMessage": { "type": "STRING" },
                "duration": { "type": "NUMBER" },
                "series": { "type": "NUMBER" },
                "rest": { "type": "NUMBER" },
                "space": { "type": "STRING" }
              }
            },
            "tacticalPrinciples": {
              "type": "ARRAY",
              "items": {
                "type": "OBJECT",
                "properties": {
                  "name": { "type": "STRING" },
                  "duration": { "type": "NUMBER" }
                }
              }
            }
          }
        }
      }
    };

    const apiKey = "";
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key=${apiKey}`;

    let retries = 0;
    const maxRetries = 5;
    let delay = 1000;

    const fetchWithRetry = async () => {
      try {
        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!response.ok) {
          throw new Error(`API call failed with status: ${response.status}`);
        }

        const result = await response.json();
        const jsonString = result?.candidates?.[0]?.content?.parts?.[0]?.text;

        if (jsonString) {
          const generatedPlan = JSON.parse(jsonString);
          setNewTraining(prevState => ({
            ...prevState,
            ...generatedPlan
          }));
          setGenerationObjectives('');
        } else {
          setGenerationError('Error: La API no devolvió una respuesta válida.');
        }

      } catch (error) {
        console.error("Error generating training session:", error);
        if (retries < maxRetries) {
          retries++;
          delay *= 2;
          setTimeout(fetchWithRetry, delay);
        } else {
          setGenerationError('Error al generar la sesión. Inténtalo de nuevo más tarde.');
        }
      } finally {
        setIsGenerating(false);
      }
    };

    fetchWithRetry();
  };
  
  // Gemini API call for explaining a tactical principle
  const explainPrinciple = async (principleName) => {
    setIsExplainingPrinciple(true);
    setPrincipleExplanation(null);

    const prompt = `Explica en detalle qué es el principio táctico de fútbol "${principleName}". Proporciona una definición clara y ejemplos de cómo se aplica en un partido. Usa un tono de tutor amistoso.`;

    const payload = {
        contents: [{ role: 'user', parts: [{ text: prompt }] }],
    };

    const apiKey = "";
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key=${apiKey}`;

    let retries = 0;
    const maxRetries = 5;
    let delay = 1000;

    const fetchWithRetry = async () => {
        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`API call failed with status: ${response.status}`);
            }

            const result = await response.json();
            const text = result?.candidates?.[0]?.content?.parts?.[0]?.text;

            if (text) {
                setPrincipleExplanation(text);
            } else {
                setPrincipleExplanation('Error: No se pudo obtener la explicación. Inténtalo de nuevo.');
            }

        } catch (error) {
            console.error("Error explaining principle:", error);
            if (retries < maxRetries) {
                retries++;
                delay *= 2;
                setTimeout(fetchWithRetry, delay);
            } else {
                setPrincipleExplanation('Error al obtener la explicación. Inténtalo de nuevo más tarde.');
            }
        } finally {
            setIsExplainingPrinciple(false);
        }
    };

    fetchWithRetry();
  };


  // Firestore functions for teams, seasons, members, trainings, and attendance
  const addTeam = async () => {
    if (newTeamName.trim() === '') return;
    try {
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      const docRef = await addDoc(collection(db, `artifacts/${appId}/public/data/teams`), { name: newTeamName, createdAt: serverTimestamp() });
      setNewTeamName('');
      setSelectedTeamId(docRef.id);
    } catch (error) { console.error('Error adding team:', error); }
  };
  
  const editTeam = async (id, newName) => {
    if (newName.trim() === '') return;
    try {
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      await setDoc(doc(db, `artifacts/${appId}/public/data/teams/${id}`), { name: newName }, { merge: true });
      setEditingTeam(null);
    } catch (error) { console.error('Error editing team:', error); }
  };
  
  const deleteTeam = async (id) => {
    try {
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      await deleteDoc(doc(db, `artifacts/${appId}/public/data/teams/${id}`));
      setSelectedTeamId('');
      setSelectedSeasonId('');
    } catch (error) { console.error('Error deleting team:', error); }
  };

  const addSeason = async () => {
    if (newSeasonName.trim() === '' || !selectedTeamId) return;
    try {
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      const docRef = await addDoc(collection(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons`), { name: newSeasonName, createdAt: serverTimestamp() });
      setNewSeasonName('');
      setSelectedSeasonId(docRef.id);
    } catch (error) { console.error('Error adding season:', error); }
  };
  
  const editSeason = async (id, newName) => {
    if (newName.trim() === '') return;
    try {
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      await setDoc(doc(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${id}`), { name: newName }, { merge: true });
      setEditingSeason(null);
    } catch (error) { console.error('Error editing season:', error); }
  };
  
  const deleteSeason = async (id) => {
    try {
      if (!selectedTeamId) return;
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      await deleteDoc(doc(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${id}`));
      setSelectedSeasonId('');
    } catch (error) { console.error('Error deleting season:', error); }
  };

  const addMember = async () => {
    if (!selectedTeamId || !selectedSeasonId) return;
    try {
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      await addDoc(collection(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/teamMembers`), {
        fullName: newMemberFullName, dateOfBirth: newMemberDateOfBirth, position: newMemberPosition, secondaryPosition: newMemberSecondaryPosition,
        dominantLeg: newMemberDominantLeg, weight: newMemberWeight, height: newMemberHeight, createdAt: serverTimestamp(), createdBy: userId,
      });
      setNewMemberFullName(''); setNewMemberDateOfBirth(''); setNewMemberPosition(''); setNewMemberSecondaryPosition('');
      setNewMemberDominantLeg(''); setNewMemberWeight(''); setNewMemberHeight('');
    } catch (error) { console.error('Error adding member:', error); }
  };

  const deleteMember = async (id) => {
    try {
      if (!selectedTeamId || !selectedSeasonId) return;
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      await deleteDoc(doc(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/teamMembers/${id}`));
    } catch (error) { console.error('Error deleting member:', error); }
  };

  const saveEditedMember = async (id) => {
    try {
      if (!selectedTeamId || !selectedSeasonId) return;
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      await setDoc(doc(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/teamMembers/${id}`), {
        fullName: editingFullName, dateOfBirth: editingDateOfBirth, position: editingPosition, secondaryPosition: editingSecondaryPosition,
        dominantLeg: editingDominantLeg, weight: editingWeight, height: editingHeight,
      }, { merge: true });
      setEditingMemberId(null);
    } catch (error) { console.error('Error updating member:', error); }
  };

  const startEditing = (member) => {
    setEditingMemberId(member.id);
    setEditingFullName(member.fullName || ''); setEditingDateOfBirth(member.dateOfBirth || '');
    setEditingPosition(member.position || ''); setEditingSecondaryPosition(member.secondaryPosition || '');
    setEditingDominantLeg(member.dominantLeg || ''); setEditingWeight(member.weight || '');
    setEditingHeight(member.height || '');
  };

  const cancelEdit = () => setEditingMemberId(null);

  const addTraining = async () => {
    if (!selectedTeamId || !selectedSeasonId) return;
    try {
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      await addDoc(collection(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/trainings`), {
        ...newTraining, createdAt: serverTimestamp(), createdBy: userId,
      });
      setNewTraining({
        date: '', time: '', place: '', macrociclo: '', mesociclo: '', microciclo: '', session: '', objectives: '', category: '',
        warmup: { description: '', rules: '', coachMessage: '', duration: '', series: '', rest: '', space: '' },
        analyticExercise: { description: '', rules: '', coachMessage: '', duration: '', series: '', rest: '', space: '' },
        introductoryExercise: { description: '', rules: '', coachMessage: '', duration: '', series: '', rest: '', space: '' },
        tacticalExercise: { description: '', rules: '', coachMessage: '', duration: '', series: '', rest: '', space: '' },
        ABP: { description: '', rules: '', coachMessage: '', duration: '', series: '', rest: '' },
        cooldown: { description: '', rules: '', coachMessage: '', duration: '', series: '', rest: '' },
        coachesRoles: '', totalVolume: '', photoLinks: '', videoLinks: '', tacticalPrinciples: []
      });
    } catch (error) { console.error('Error adding training session:', error); }
  };

  const deleteTraining = async (id) => {
    try {
      if (!selectedTeamId || !selectedSeasonId) return;
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      await deleteDoc(doc(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/trainings/${id}`));
    } catch (error) { console.error('Error deleting training session:', error); }
  };

  const startEditingTraining = (training) => {
    setEditingTrainingId(training.id);
    setNewTraining(training);
  };

  const saveEditedTraining = async (id) => {
    try {
      if (!selectedTeamId || !selectedSeasonId) return;
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      await setDoc(doc(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/trainings/${id}`), newTraining, { merge: true });
      cancelTrainingEdit();
    } catch (error) { console.error('Error updating training session:', error); }
  };

  const cancelTrainingEdit = () => {
    setEditingTrainingId(null);
    setNewTraining({
      date: '', time: '', place: '', macrociclo: '', mesociclo: '', microciclo: '', session: '', objectives: '', category: '',
      warmup: { description: '', rules: '', coachMessage: '', duration: '', series: '', rest: '', space: '' },
      analyticExercise: { description: '', rules: '', coachMessage: '', duration: '', series: '', rest: '', space: '' },
      introductoryExercise: { description: '', rules: '', coachMessage: '', duration: '', series: '', rest: '', space: '' },
      tacticalExercise: { description: '', rules: '', coachMessage: '', duration: '', series: '', rest: '', space: '' },
      ABP: { description: '', rules: '', coachMessage: '', duration: '', series: '', rest: '' },
      cooldown: { description: '', rules: '', coachMessage: '', duration: '', series: '', rest: '' },
      coachesRoles: '', totalVolume: '', photoLinks: '', videoLinks: '', tacticalPrinciples: []
    });
  };

  const handleExerciseChange = (exerciseType, field, value) => {
    setNewTraining(prevState => ({
      ...prevState,
      [exerciseType]: { ...prevState[exerciseType], [field]: value }
    }));
  };
  
  const addTacticalPrincipleToTraining = () => {
    setNewTraining(prevState => ({
      ...prevState,
      tacticalPrinciples: [...prevState.tacticalPrinciples, { name: '', duration: '' }]
    }));
  };
  
  const handleTacticalPrincipleChange = (index, field, value) => {
    const updatedPrinciples = [...newTraining.tacticalPrinciples];
    updatedPrinciples[index][field] = value;
    setNewTraining(prevState => ({
      ...prevState,
      tacticalPrinciples: updatedPrinciples
    }));
  };

  const markAttendance = async (memberFullName, status) => {
    if (!selectedTeamId || !selectedSeasonId || !db) return;
    try {
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      await setDoc(doc(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/attendance/${todayDate}`), {
        [memberFullName]: { status, justification: status === 'Ausente' ? 'Sin justificar' : null }
      }, { merge: true });
    } catch (error) { console.error('Error updating attendance:', error); }
  };

  const justifyAbsence = async (memberFullName, justification) => {
    if (!selectedTeamId || !selectedSeasonId || !db) return;
    try {
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      await setDoc(doc(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/attendance/${todayDate}`), {
        [memberFullName]: { status: 'Ausente', justification }
      }, { merge: true });
    } catch (error) { console.error('Error justifying absence:', error); }
  };

  const addPrinciple = async () => {
    if (!selectedTeamId || !selectedSeasonId || newPrincipleName.trim() === '') return;
    try {
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      await addDoc(collection(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/tacticalPrinciples`), {
        name: newPrincipleName, createdAt: serverTimestamp(), createdBy: userId,
      });
      setNewPrincipleName('');
    } catch (error) { console.error('Error adding tactical principle:', error); }
  };

  const deletePrinciple = async (id) => {
    try {
      if (!selectedTeamId || !selectedSeasonId) return;
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      await deleteDoc(doc(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/tacticalPrinciples/${id}`));
    } catch (error) { console.error('Error deleting tactical principle:', error); }
  };

  const startEditingPrinciple = (principle) => {
    setEditingPrincipleId(principle.id);
    setEditingPrincipleName(principle.name);
  };

  const saveEditedPrinciple = async (id) => {
    try {
      if (!selectedTeamId || !selectedSeasonId) return;
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      await setDoc(doc(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/tacticalPrinciples/${id}`), {
        name: editingPrincipleName,
      }, { merge: true });
      setEditingPrincipleId(null);
    } catch (error) { console.error('Error updating tactical principle:', error); }
  };

  const cancelPrincipleEdit = () => setEditingPrincipleId(null);
  
  // Functions for training videos
  const handleVideoInputChange = (e) => {
    const { name, value } = e.target;
    if (editingVideo) {
      setEditingVideo(prevState => ({ ...prevState, [name]: value }));
    } else {
      setNewVideo(prevState => ({ ...prevState, [name]: value }));
    }
  };

  const addVideo = async (e) => {
    e.preventDefault();
    if (!newVideo.name || !newVideo.url || !newVideo.category || !userId) {
        setVideoMessage('Por favor, completa todos los campos.');
        return;
    }

    const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
    const collectionName = activeVideoSection === 'mis_entrenamientos' ?
        `artifacts/${appId}/users/${userId}/mis_entrenamientos` :
        `artifacts/${appId}/public/data/otros_entrenamientos`;

    try {
        await addDoc(collection(db, collectionName), {
            ...newVideo,
            timestamp: Date.now()
        });
        setNewVideo({ name: '', url: '', category: newVideo.category }); // Reset form
        setVideoMessage('¡Video guardado con éxito!');
    } catch (e) {
        console.error('Error adding document: ', e);
        setVideoMessage('Error al guardar el video. Inténtalo de nuevo.');
    }
  };

  const deleteVideo = async (id) => {
    const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
    const collectionName = activeVideoSection === 'mis_entrenamientos' ?
        `artifacts/${appId}/users/${userId}/mis_entrenamientos` :
        `artifacts/${appId}/public/data/otros_entrenamientos`;

    try {
        await deleteDoc(doc(db, collectionName, id));
        setVideoMessage('Video eliminado correctamente.');
    } catch (e) {
        console.error('Error removing document: ', e);
        setVideoMessage('Error al eliminar el video. Inténtalo de nuevo.');
    }
  };
  
  const startEditingVideo = (video) => {
    setEditingVideo({ ...video });
  };

  const saveEditedVideo = async (e) => {
    e.preventDefault();
    if (!editingVideo.name || !editingVideo.url || !editingVideo.category) {
      setVideoMessage('Por favor, completa todos los campos.');
      return;
    }

    const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
    const collectionName = activeVideoSection === 'mis_entrenamientos' ?
        `artifacts/${appId}/users/${userId}/mis_entrenamientos` :
        `artifacts/${appId}/public/data/otros_entrenamientos`;
    
    try {
      await setDoc(doc(db, collectionName, editingVideo.id), {
        name: editingVideo.name,
        url: editingVideo.url,
        category: editingVideo.category,
      }, { merge: true });
      setEditingVideo(null);
      setVideoMessage('Video actualizado con éxito.');
    } catch (e) {
      console.error('Error updating document: ', e);
      setVideoMessage('Error al actualizar el video. Inténtalo de nuevo.');
    }
  };

  const cancelVideoEdit = () => {
    setEditingVideo(null);
  };
  
  // Functions for Match Plans
  const handleMatchPlanChange = (e) => {
    const { name, value } = e.target;
    setNewMatchPlan(prevState => ({ ...prevState, [name]: value }));
  };
  
  const addMatchPlan = async () => {
    if (!selectedTeamId || !selectedSeasonId || !newMatchPlan.rival.trim()) return;
    try {
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      await addDoc(collection(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/matchPlans`), {
        ...newMatchPlan,
        createdAt: serverTimestamp(),
        createdBy: userId,
      });
      setNewMatchPlan({
        rival: '', date: '', place: '', time: '', rivalStrengths: '', rivalWeaknesses: '',
        offensiveOrganization: '', defensiveOrganization: '', offensiveTransition: '',
        defensiveTransition: '', offensiveABP: '', defensiveABP: '', additionalNotes: '', videoLink: ''
      });
    } catch (e) { console.error('Error adding match plan:', e); }
  };
  
  const deleteMatchPlan = async (id) => {
    try {
      if (!selectedTeamId || !selectedSeasonId) return;
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      await deleteDoc(doc(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/matchPlans/${id}`));
    } catch (e) { console.error('Error deleting match plan:', e); }
  };
  
  const startEditingMatchPlan = (plan) => {
    setEditingMatchPlanId(plan.id);
    setNewMatchPlan(plan);
  };
  
  const saveEditedMatchPlan = async (id) => {
    try {
      if (!selectedTeamId || !selectedSeasonId) return;
      const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      await setDoc(doc(db, `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/matchPlans/${id}`), newMatchPlan, { merge: true });
      cancelMatchPlanEdit();
    } catch (e) { console.error('Error updating match plan:', e); }
  };
  
  const cancelMatchPlanEdit = () => {
    setEditingMatchPlanId(null);
    setNewMatchPlan({
      rival: '', date: '', place: '', time: '', rivalStrengths: '', rivalWeaknesses: '',
      offensiveOrganization: '', defensiveOrganization: '', offensiveTransition: '',
      defensiveTransition: '', offensiveABP: '', defensiveABP: '', additionalNotes: '', videoLink: ''
    });
  };

  // Functions for Video Analysis
  const handleAnalysisChange = (e) => {
    const { name, value } = e.target;
    setNewAnalysis(prev => ({ ...prev, [name]: value }));
  };

  const handleNestedAnalysisChange = (parent, child, value) => {
    setNewAnalysis(prev => ({
      ...prev,
      [parent]: {
        ...prev[parent],
        [child]: value
      }
    }));
  };

  const addOrUpdateAnalysis = async () => {
    if (!selectedTeamId || !selectedSeasonId || !newAnalysis.equipoAnalizado.trim()) return;
    const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
    const collectionPath = `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/videoAnalysis`;
    try {
      if (editingAnalysisId) {
        await setDoc(doc(db, collectionPath, editingAnalysisId), { ...newAnalysis, type: activeAnalysisSection }, { merge: true });
      } else {
        await addDoc(collection(db, collectionPath), { ...newAnalysis, type: activeAnalysisSection, createdAt: serverTimestamp() });
      }
      setNewAnalysis(initialAnalysisState);
      setEditingAnalysisId(null);
    } catch (e) { console.error('Error saving analysis:', e); }
  };

  const deleteAnalysis = async (id) => {
    if (!selectedTeamId || !selectedSeasonId) return;
    const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
    const collectionPath = `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/videoAnalysis`;
    try {
      await deleteDoc(doc(db, collectionPath, id));
    } catch (e) { console.error('Error deleting analysis:', e); }
  };

  const startEditingAnalysis = (analysis) => {
    setEditingAnalysisId(analysis.id);
    // Ensure nested object exists for backward compatibility and handle renamed fields
    const analysisData = {
      ...initialAnalysisState,
      ...analysis,
      abpOfensivo: analysis.abpOfensivo || analysis.abpOfensivos || '', // Handle old field name
      abpDefensivo: analysis.abpDefensivo || analysis.abpDefensivos || '', // Handle old field name
      organizacionOfensiva: {
        ...initialAnalysisState.organizacionOfensiva,
        ...(analysis.organizacionOfensiva || {})
      }
    };
    setNewAnalysis(analysisData);
  };

  const cancelEditingAnalysis = () => {
    setEditingAnalysisId(null);
    setNewAnalysis(initialAnalysisState);
  };

  // Functions for Matches
  const handleMatchChange = (e) => {
    const { name, value } = e.target;
    setNewMatch(prev => ({ ...prev, [name]: value }));
  };

  const handleMatchObservacionesChange = (field, value) => {
    setNewMatch(prev => ({
      ...prev,
      observaciones: {
        ...prev.observaciones,
        [field]: value
      }
    }));
  };
  
  const addEventToMatch = () => {
    if (!newEvent.player || !newEvent.type) return;
    setNewMatch(prev => ({ ...prev, events: [...prev.events, newEvent] }));
    setNewEvent({ player: '', type: '', detail: '' });
  };
  
  const removeEventFromMatch = (index) => {
    setNewMatch(prev => ({
      ...prev,
      events: prev.events.filter((_, i) => i !== index)
    }));
  };

  const addOrUpdateMatch = async () => {
    if (!selectedTeamId || !selectedSeasonId || !newMatch.rival.trim()) return;
    const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
    const collectionPath = `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/matches`;
    try {
      if (editingMatchId) {
        await setDoc(doc(db, collectionPath, editingMatchId), { ...newMatch }, { merge: true });
      } else {
        await addDoc(collection(db, collectionPath), { ...newMatch, createdAt: serverTimestamp() });
      }
      setNewMatch(initialMatchState);
      setEditingMatchId(null);
    } catch (e) { console.error('Error saving match:', e); }
  };

  const deleteMatch = async (id) => {
    if (!selectedTeamId || !selectedSeasonId) return;
    const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
    const collectionPath = `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/matches`;
    try {
      await deleteDoc(doc(db, collectionPath, id));
    } catch (e) { console.error('Error deleting match:', e); }
  };

  const startEditingMatch = (match) => {
    setEditingMatchId(match.id);
    setNewMatch({ ...initialMatchState, ...match });
  };

  const cancelEditingMatch = () => {
    setEditingMatchId(null);
    setNewMatch(initialMatchState);
  };
  
  // Functions for Scouting Reports
  const calculateAge = (dob) => {
    if (!dob) return '';
    const birthDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  useEffect(() => {
    if (newScoutingReport.fechaNacimiento) {
      const age = calculateAge(newScoutingReport.fechaNacimiento);
      setNewScoutingReport(prev => ({ ...prev, edad: age }));
    }
  }, [newScoutingReport.fechaNacimiento]);

  const handleScoutingChange = (e) => {
    const { name, value } = e.target;
    setNewScoutingReport(prev => ({ ...prev, [name]: value }));
  };

  const handleNestedScoutingChange = (category, field, value) => {
    setNewScoutingReport(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [field]: value
      }
    }));
  };
  
  const addOrUpdateScoutingReport = async () => {
    if (!selectedTeamId || !selectedSeasonId || !newScoutingReport.nombreJugador.trim()) return;
    const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
    const collectionPath = `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/scoutingReports`;
    try {
      if (editingScoutingReportId) {
        await setDoc(doc(db, collectionPath, editingScoutingReportId), { ...newScoutingReport }, { merge: true });
      } else {
        await addDoc(collection(db, collectionPath), { ...newScoutingReport, createdAt: serverTimestamp() });
      }
      setNewScoutingReport(initialScoutingState);
      setEditingScoutingReportId(null);
    } catch (e) { console.error('Error saving scouting report:', e); }
  };
  
  const deleteScoutingReport = async (id) => {
    if (!selectedTeamId || !selectedSeasonId) return;
    const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
    const collectionPath = `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/scoutingReports`;
    try {
      await deleteDoc(doc(db, collectionPath, id));
    } catch (e) { console.error('Error deleting scouting report:', e); }
  };
  
  const startEditingScoutingReport = (report) => {
    setEditingScoutingReportId(report.id);
    setNewScoutingReport({ ...initialScoutingState, ...report });
  };
  
  const cancelEditingScoutingReport = () => {
    setEditingScoutingReportId(null);
    setNewScoutingReport(initialScoutingState);
  };
  
  // Functions for Match Videos
  const handleMatchVideoChange = (e) => {
    const { name, value } = e.target;
    setNewMatchVideo(prev => ({ ...prev, [name]: value }));
  };

  const addOrUpdateMatchVideo = async () => {
    if (!selectedTeamId || !selectedSeasonId || !newMatchVideo.teams.trim() || !newMatchVideo.link.trim()) return;
    const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
    const collectionPath = `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/matchVideos`;
    try {
      if (editingMatchVideo?.id) {
        await setDoc(doc(db, collectionPath, editingMatchVideo.id), { ...newMatchVideo, type: activeMatchVideoSection }, { merge: true });
      } else {
        await addDoc(collection(db, collectionPath), { ...newMatchVideo, type: activeMatchVideoSection, createdAt: serverTimestamp() });
      }
      setNewMatchVideo({ teams: '', link: '' });
      setEditingMatchVideo(null);
    } catch (e) { console.error('Error saving match video:', e); }
  };

  const deleteMatchVideo = async (id) => {
    if (!selectedTeamId || !selectedSeasonId) return;
    const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
    const collectionPath = `artifacts/${appId}/public/data/teams/${selectedTeamId}/seasons/${selectedSeasonId}/matchVideos`;
    try {
      await deleteDoc(doc(db, collectionPath, id));
    } catch (e) { console.error('Error deleting match video:', e); }
  };

  const startEditingMatchVideo = (video) => {
    setEditingMatchVideo(video);
    setNewMatchVideo({ teams: video.teams, link: video.link });
  };

  const cancelEditingMatchVideo = () => {
    setEditingMatchVideo(null);
    setNewMatchVideo({ teams: '', link: '' });
  };


  if (!isAuthReady) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <p className="text-xl font-medium text-gray-700">Autenticando...</p>
      </div>
    );
  }

  // Component to render the list of videos grouped by category
  const VideoList = ({ videos }) => {
    const sortedCategories = categories.filter(cat => videos[cat] && videos[cat].length > 0);

    if (sortedCategories.length === 0) {
        return <p className="text-gray-400 mt-4">No hay videos en esta sección.</p>;
    }

    return (
        <div className="mt-6 space-y-8">
            {sortedCategories.map(category => (
                <div key={category} className="bg-gray-100 p-6 rounded-xl shadow-lg border">
                    <h3 className="text-2xl font-bold text-gray-800 mb-4">{category}</h3>
                    <ul className="space-y-4">
                        {videos[category].map(video => (
                            <li key={video.id} className="flex flex-col sm:flex-row items-start sm:items-center justify-between bg-white p-4 rounded-lg shadow-sm">
                                <div className="flex-1 mb-2 sm:mb-0">
                                    <p className="font-semibold text-gray-800">{video.name}</p>
                                    <a
                                        href={video.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-blue-600 hover:text-blue-500 transition-colors duration-200 text-sm break-all"
                                    >
                                        Ver video
                                    </a>
                                </div>
                                <div className="flex gap-2">
                                  <button
                                      onClick={() => startEditingVideo(video)}
                                      className="bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-2 px-4 rounded-full transition-colors duration-200"
                                  >
                                      Editar
                                  </button>
                                  <button
                                      onClick={() => deleteVideo(video.id)}
                                      className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded-full transition-colors duration-200"
                                  >
                                      Eliminar
                                  </button>
                                </div>
                            </li>
                        ))}
                    </ul>
                </div>
            ))}
        </div>
    );
  };

  // Modal to display member details
  const renderMemberDetailsModal = () => {
    if (!viewingMember) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50 p-4">
            <div className="bg-white p-8 rounded-2xl shadow-2xl max-w-md w-full transform transition-all">
                <h2 className="text-3xl font-bold mb-6 text-gray-800 border-b pb-4">{viewingMember.fullName}</h2>
                <div className="space-y-3 text-gray-700">
                    <p><strong>Fecha de Nacimiento:</strong> <span className="font-medium">{viewingMember.dateOfBirth || 'No especificado'}</span></p>
                    <p><strong>Puesto:</strong> <span className="font-medium">{viewingMember.position || 'No especificado'}</span></p>
                    <p><strong>Puesto Secundario:</strong> <span className="font-medium">{viewingMember.secondaryPosition || 'No especificado'}</span></p>
                    <p><strong>Pierna Hábil:</strong> <span className="font-medium">{viewingMember.dominantLeg || 'No especificado'}</span></p>
                    <p><strong>Peso:</strong> <span className="font-medium">{viewingMember.weight ? `${viewingMember.weight} kg` : 'No especificado'}</span></p>
                    <p><strong>Talla:</strong> <span className="font-medium">{viewingMember.height ? `${viewingMember.height} cm` : 'No especificado'}</span></p>
                </div>
                <button
                    onClick={() => setViewingMember(null)}
                    className="mt-8 w-full bg-gray-600 text-white py-3 px-4 rounded-lg shadow-md hover:bg-gray-700 transition-colors duration-300 font-semibold"
                >
                    Cerrar
                </button>
            </div>
        </div>
    );
  };
  
  // Modal to display training details
  const renderTrainingDetailsModal = () => {
    if (!viewingTraining) return null;
  
    const ExerciseDetail = ({ title, exercise }) => {
      if (!exercise || !exercise.description) return null;
      return (
        <div className="mt-4 pt-4 border-t">
          <h4 className="text-xl font-bold text-gray-800 mb-2">{title}</h4>
          <p><strong>Descripción:</strong> {exercise.description || 'N/A'}</p>
          <p><strong>Reglas:</strong> {exercise.rules || 'N/A'}</p>
          <p><strong>Mensaje del Entrenador:</strong> {exercise.coachMessage || 'N/A'}</p>
          <p><strong>Duración:</strong> {exercise.duration || 'N/A'} min</p>
          <p><strong>Series:</strong> {exercise.series || 'N/A'}</p>
          <p><strong>Descanso:</strong> {exercise.rest || 'N/A'} min</p>
          <p><strong>Espacio:</strong> {exercise.space || 'N/A'}</p>
        </div>
      );
    };
  
    return (
      <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50 p-4">
        <div className="bg-white p-8 rounded-2xl shadow-2xl max-w-2xl w-full transform transition-all max-h-[90vh] overflow-y-auto">
          <h2 className="text-3xl font-bold mb-4 text-gray-800 border-b pb-4">Detalles del Entrenamiento</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4 mb-4">
            <div><strong>Fecha:</strong> <span className="font-medium">{viewingTraining.date || 'N/A'}</span></div>
            <div><strong>Hora:</strong> <span className="font-medium">{viewingTraining.time || 'N/A'}</span></div>
            <div><strong>Lugar:</strong> <span className="font-medium">{viewingTraining.place || 'N/A'}</span></div>
            <div><strong>Sesión:</strong> <span className="font-medium">{viewingTraining.session || 'N/A'}</span></div>
            <div><strong>Categoría:</strong> <span className="font-medium">{viewingTraining.category || 'N/A'}</span></div>
            <div><strong>Macrociclo:</strong> <span className="font-medium">{viewingTraining.macrociclo || 'N/A'}</span></div>
            <div><strong>Mesociclo:</strong> <span className="font-medium">{viewingTraining.mesociclo || 'N/A'}</span></div>
            <div className="md:col-span-2"><strong>Microciclo:</strong> <span className="font-medium">{viewingTraining.microciclo || 'N/A'}</span></div>
          </div>
  
          <div className="border-t pt-4 mb-4">
            <h4 className="text-lg font-bold text-gray-800">Objetivos:</h4>
            <p className="font-medium whitespace-pre-wrap">{viewingTraining.objectives || 'N/A'}</p>
          </div>
  
          {viewingTraining.tacticalPrinciples && viewingTraining.tacticalPrinciples.length > 0 && (
            <div className="border-t pt-4 mb-4">
              <h4 className="text-lg font-bold text-gray-800">Principios Tácticos:</h4>
              <ul className="list-disc list-inside">
                {viewingTraining.tacticalPrinciples.map((p, idx) => (
                  <li key={idx} className="font-medium">{p.name}: {p.duration} min</li>
                ))}
              </ul>
            </div>
          )}
  
          <ExerciseDetail title="Entrada en Calor" exercise={viewingTraining.warmup} />
          <ExerciseDetail title="Ejercicio Analítico" exercise={viewingTraining.analyticExercise} />
          <ExerciseDetail title="Ejercicio Introductorio" exercise={viewingTraining.introductoryExercise} />
          <ExerciseDetail title="Ejercicio Táctico" exercise={viewingTraining.tacticalExercise} />
          <ExerciseDetail title="ABP" exercise={viewingTraining.ABP} />
          <ExerciseDetail title="Vuelta a la Calma" exercise={viewingTraining.cooldown} />

          <div className="mt-4 pt-4 border-t">
            <h4 className="text-xl font-bold text-gray-800 mb-2">Información Adicional</h4>
            <p><strong>Roles de Entrenadores:</strong> {viewingTraining.coachesRoles || 'N/A'}</p>
            <p><strong>Volumen Total:</strong> {viewingTraining.totalVolume || 'N/A'}</p>
            <p><strong>Fotos:</strong> <a href={viewingTraining.photoLinks} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline break-all">{viewingTraining.photoLinks || 'N/A'}</a></p>
            <p><strong>Videos:</strong> <a href={viewingTraining.videoLinks} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline break-all">{viewingTraining.videoLinks || 'N/A'}</a></p>
          </div>
  
          <button
            onClick={() => setViewingTraining(null)}
            className="mt-8 w-full bg-gray-600 text-white py-3 px-4 rounded-lg shadow-md hover:bg-gray-700 transition-colors duration-300 font-semibold"
          >
            Cerrar
          </button>
        </div>
      </div>
    );
  };

  // Modal to display video analysis details
  const renderAnalysisDetailsModal = () => {
    if (!viewingAnalysis) return null;
    return (
      <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50 p-4">
        <div className="bg-white p-8 rounded-2xl shadow-2xl max-w-2xl w-full transform transition-all max-h-[90vh] overflow-y-auto">
          <h2 className="text-3xl font-bold mb-4 text-gray-800 border-b pb-4">Detalles del Análisis de Video</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4 mb-4">
            <div><strong>Equipo Analizado:</strong> <span className="font-medium">{viewingAnalysis.equipoAnalizado || 'N/A'}</span></div>
            <div><strong>Rival:</strong> <span className="font-medium">{viewingAnalysis.rival || 'N/A'}</span></div>
            <div><strong>Lugar:</strong> <span className="font-medium">{viewingAnalysis.lugar || 'N/A'}</span></div>
            <div><strong>Fecha del Informe:</strong> <span className="font-medium">{viewingAnalysis.fechaInforme || 'N/A'}</span></div>
          </div>

          <div className="border-t pt-4 mb-4">
            <h4 className="text-lg font-bold text-gray-800">Sistema de Juego:</h4>
            <p className="font-medium whitespace-pre-wrap">{viewingAnalysis.sistemaJuego || 'N/A'}</p>
          </div>

          <div className="border-t pt-4 mb-4">
            <h4 className="text-lg font-bold text-gray-800">Momentos del Juego:</h4>
            <div className="ml-4 mt-2">
              <h5 className="font-semibold">Organización Ofensiva:</h5>
              <p className="ml-4"><strong>Inicio:</strong> {viewingAnalysis.organizacionOfensiva?.inicio || 'N/A'}</p>
              <p className="ml-4"><strong>Creación y Progresión:</strong> {viewingAnalysis.organizacionOfensiva?.creacion || 'N/A'}</p>
              <p className="ml-4"><strong>Finalización:</strong> {viewingAnalysis.organizacionOfensiva?.finalizacion || 'N/A'}</p>
              <h5 className="font-semibold mt-2">Organización Defensiva:</h5><p className="ml-4">{viewingAnalysis.organizacionDefensiva || 'N/A'}</p>
              <h5 className="font-semibold mt-2">Transición Ofensiva:</h5><p className="ml-4">{viewingAnalysis.transicionOfensiva || 'N/A'}</p>
              <h5 className="font-semibold mt-2">Transición Defensiva:</h5><p className="ml-4">{viewingAnalysis.transicionDefensiva || 'N/A'}</p>
              <h5 className="font-semibold mt-2">ABP Ofensivo:</h5><p className="ml-4">{viewingAnalysis.abpOfensivo || viewingAnalysis.abpOfensivos || 'N/A'}</p>
              <h5 className="font-semibold mt-2">ABP Defensivo:</h5><p className="ml-4">{viewingAnalysis.abpDefensivo || viewingAnalysis.abpDefensivos || 'N/A'}</p>
              <h5 className="font-semibold mt-2">Laterales:</h5><p className="ml-4">{viewingAnalysis.laterales || 'N/A'}</p>
            </div>
          </div>
          
          <div className="border-t pt-4 mb-4">
            <h4 className="text-lg font-bold text-gray-800">Fortalezas:</h4>
            <p className="font-medium whitespace-pre-wrap">{viewingAnalysis.fortalezas || 'N/A'}</p>
          </div>
          <div className="border-t pt-4 mb-4">
            <h4 className="text-lg font-bold text-gray-800">Debilidades:</h4>
            <p className="font-medium whitespace-pre-wrap">{viewingAnalysis.debilidades || 'N/A'}</p>
          </div>
          
          <div className="border-t pt-4 mb-4">
            <h4 className="text-lg font-bold text-gray-800">Notas Adicionales:</h4>
            <p className="font-medium whitespace-pre-wrap">{viewingAnalysis.notasAdicionales || 'N/A'}</p>
          </div>
          <div className="border-t pt-4">
            <strong>Enlace de Video:</strong> <a href={viewingAnalysis.enlaceVideo} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline break-all">{viewingAnalysis.enlaceVideo || 'N/A'}</a>
          </div>
          <button
            onClick={() => setViewingAnalysis(null)}
            className="mt-8 w-full bg-gray-600 text-white py-3 px-4 rounded-lg shadow-md hover:bg-gray-700 transition-colors duration-300 font-semibold"
          >
            Cerrar
          </button>
        </div>
      </div>
    );
  };

  // Modal to display match details
  const renderMatchDetailsModal = () => {
    if (!viewingMatch) return null;
    return (
      <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50 p-4">
        <div className="bg-white p-8 rounded-2xl shadow-2xl max-w-2xl w-full transform transition-all max-h-[90vh] overflow-y-auto">
          <h2 className="text-3xl font-bold mb-4 text-gray-800 border-b pb-4">Detalles del Partido</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4 mb-4">
            <div><strong>Rival:</strong> <span className="font-medium">{viewingMatch.rival || 'N/A'}</span></div>
            <div><strong>Resultado:</strong> <span className="font-medium">{viewingMatch.resultado || 'N/A'}</span></div>
            <div><strong>Fecha:</strong> <span className="font-medium">{viewingMatch.fecha || 'N/A'}</span></div>
            <div><strong>Hora:</strong> <span className="font-medium">{viewingMatch.hora || 'N/A'}</span></div>
            <div><strong>Lugar:</strong> <span className="font-medium">{viewingMatch.lugar || 'N/A'}</span></div>
            <div><strong>Sistema Utilizado:</strong> <span className="font-medium">{viewingMatch.sistemaUtilizado || 'N/A'}</span></div>
          </div>
          <div className="border-t pt-4 mb-4">
            <h4 className="text-lg font-bold text-gray-800">Titulares:</h4>
            <p className="font-medium whitespace-pre-wrap">{viewingMatch.titulares || 'N/A'}</p>
          </div>
          <div className="border-t pt-4 mb-4">
            <h4 className="text-lg font-bold text-gray-800">Suplentes:</h4>
            <p className="font-medium whitespace-pre-wrap">{viewingMatch.suplentes || 'N/A'}</p>
          </div>
          <div className="border-t pt-4 mb-4">
            <h4 className="text-lg font-bold text-gray-800">Eventos del Partido:</h4>
            <ul className="list-disc list-inside">
              {viewingMatch.events && viewingMatch.events.map((event, index) => (
                <li key={index}>{event.player} - {eventTypes.find(e => e.value === event.type)?.label} {event.detail && `(${event.detail})`}</li>
              ))}
            </ul>
          </div>
          <div className="border-t pt-4 mb-4">
            <h4 className="text-lg font-bold text-gray-800">Observaciones:</h4>
            <p className="ml-4"><strong>Organización Ofensiva:</strong> {viewingMatch.observaciones?.organizacionOfensiva || 'N/A'}</p>
            <p className="ml-4"><strong>Organización Defensiva:</strong> {viewingMatch.observaciones?.organizacionDefensiva || 'N/A'}</p>
            <p className="ml-4"><strong>Transición Ofensiva:</strong> {viewingMatch.observaciones?.transicionOfensiva || 'N/A'}</p>
            <p className="ml-4"><strong>Transición Defensiva:</strong> {viewingMatch.observaciones?.transicionDefensiva || 'N/A'}</p>
            <p className="ml-4"><strong>ABP Ofensivo:</strong> {viewingMatch.observaciones?.abpOfensivo || 'N/A'}</p>
            <p className="ml-4"><strong>ABP Defensivo:</strong> {viewingMatch.observaciones?.abpDefensivo || 'N/A'}</p>
            <p className="ml-4"><strong>Notas Adicionales:</strong> {viewingMatch.observaciones?.notasAdicionales || 'N/A'}</p>
          </div>
          <div className="border-t pt-4">
            <strong>Enlace de Video:</strong> <a href={viewingMatch.enlaceVideo} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline break-all">{viewingMatch.enlaceVideo || 'N/A'}</a>
          </div>
          <button
            onClick={() => setViewingMatch(null)}
            className="mt-8 w-full bg-gray-600 text-white py-3 px-4 rounded-lg shadow-md hover:bg-gray-700 transition-colors duration-300 font-semibold"
          >
            Cerrar
          </button>
        </div>
      </div>
    );
  };
  
  // Modal to display scouting report details
  const renderScoutingReportDetailsModal = () => {
    if (!viewingScoutingReport) return null;

    const DetailSection = ({ title, data }) => (
      <div className="border-t pt-4 mb-4">
        <h4 className="text-lg font-bold text-gray-800 mb-2">{title}</h4>
        {Object.entries(data).map(([key, value]) => {
          const formattedKey = key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
          return <p key={key} className="ml-4"><strong>{formattedKey}:</strong> {value || 'N/A'}</p>;
        })}
      </div>
    );

    return (
      <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50 p-4">
        <div className="bg-white p-8 rounded-2xl shadow-2xl max-w-2xl w-full transform transition-all max-h-[90vh] overflow-y-auto">
          <h2 className="text-3xl font-bold mb-4 text-gray-800 border-b pb-4">Informe de Scouting: {viewingScoutingReport.nombreJugador}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4 mb-4">
            <div><strong>Fecha de Nacimiento:</strong> <span className="font-medium">{viewingScoutingReport.fechaNacimiento || 'N/A'}</span></div>
            <div><strong>Edad:</strong> <span className="font-medium">{viewingScoutingReport.edad || 'N/A'}</span></div>
            <div><strong>Categoría:</strong> <span className="font-medium">{viewingScoutingReport.categoria || 'N/A'}</span></div>
            <div><strong>Club:</strong> <span className="font-medium">{viewingScoutingReport.club || 'N/A'}</span></div>
            <div><strong>Posición Principal:</strong> <span className="font-medium">{viewingScoutingReport.posicionPrincipal || 'N/A'}</span></div>
            <div><strong>Posición Secundaria:</strong> <span className="font-medium">{viewingScoutingReport.posicionSecundaria || 'N/A'}</span></div>
            <div><strong>Pierna Hábil:</strong> <span className="font-medium">{viewingScoutingReport.piernaHabil || 'N/A'}</span></div>
            <div><strong>Talla:</strong> <span className="font-medium">{viewingScoutingReport.talla ? `${viewingScoutingReport.talla} cm` : 'N/A'}</span></div>
            <div><strong>Peso:</strong> <span className="font-medium">{viewingScoutingReport.peso ? `${viewingScoutingReport.peso} kg` : 'N/A'}</span></div>
            <div><strong>Fecha del Informe:</strong> <span className="font-medium">{viewingScoutingReport.fechaInforme || 'N/A'}</span></div>
          </div>
          
          <DetailSection title="Fortalezas" data={viewingScoutingReport.fortalezas} />
          <DetailSection title="Debilidades" data={viewingScoutingReport.debilidades} />

          <div className="border-t pt-4 mb-4">
            <h4 className="text-lg font-bold text-gray-800">Historial de Lesiones:</h4>
            <p className="font-medium whitespace-pre-wrap">{viewingScoutingReport.historialLesiones || 'N/A'}</p>
          </div>

          <div className="border-t pt-4 mb-4">
            <h4 className="text-lg font-bold text-gray-800">Notas Adicionales:</h4>
            <p className="font-medium whitespace-pre-wrap">{viewingScoutingReport.notasAdicionales || 'N/A'}</p>
          </div>
          <div className="border-t pt-4">
            <strong>Enlace de Video:</strong> <a href={viewingScoutingReport.enlaceVideo} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline break-all">{viewingScoutingReport.enlaceVideo || 'N/A'}</a>
          </div>
          <button
            onClick={() => setViewingScoutingReport(null)}
            className="mt-8 w-full bg-gray-600 text-white py-3 px-4 rounded-lg shadow-md hover:bg-gray-700 transition-colors duration-300 font-semibold"
          >
            Cerrar
          </button>
        </div>
      </div>
    );
  };

  // Render Section components
  const renderGestionSection = () => (
    <div className="mb-8 border-t pt-8">
      <h2 className="text-2xl font-semibold text-gray-800 mb-2">Equipos y Temporadas</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Team Management */}
        <div className="flex flex-col">
          <div className="flex gap-2">
            <input type="text" value={newTeamName} onChange={(e) => setNewTeamName(e.target.value)} placeholder="Nuevo equipo" className="flex-1 p-3 border rounded-lg" />
            <button onClick={addTeam} className="bg-purple-600 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-purple-700">Crear Equipo</button>
          </div>
          <div className="mt-4">
            <h3 className="font-semibold mb-2">Lista de Equipos</h3>
            {teams.length === 0 ? <p className="text-sm text-gray-500">No hay equipos creados.</p> : (
              <ul className="space-y-2">
                {teams.map(t => (
                  <li key={t.id} className="flex items-center justify-between p-2 bg-gray-100 rounded-lg">
                    {editingTeam?.id === t.id ? (
                      <div className="flex-1 flex gap-2">
                        <input type="text" value={editingTeam.name} onChange={(e) => setEditingTeam({ ...editingTeam, name: e.target.value })} className="flex-1 p-1 border rounded-md" />
                        <button onClick={() => editTeam(t.id, editingTeam.name)} className="text-green-600">✔</button>
                        <button onClick={() => setEditingTeam(null)} className="text-gray-500">✖</button>
                      </div>
                    ) : (
                      <>
                        <span className={`flex-1 cursor-pointer ${selectedTeamId === t.id ? 'font-bold' : ''}`} onClick={() => { setSelectedTeamId(t.id); setSelectedSeasonId(''); }}>{t.name}</span>
                        <div className="flex gap-2">
                          <button onClick={() => setEditingTeam(t)} className="text-yellow-600 hover:text-yellow-700">Editar</button>
                          <button onClick={() => deleteTeam(t.id)} className="text-red-600 hover:text-red-700">Eliminar</button>
                        </div>
                      </>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
        {/* Season Management */}
        <div className="flex flex-col">
          <div className="flex gap-2">
            <input type="text" value={newSeasonName} onChange={(e) => setNewSeasonName(e.target.value)} placeholder="Nueva temporada" className="flex-1 p-3 border rounded-lg" disabled={!selectedTeamId} />
            <button onClick={addSeason} className="bg-purple-600 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-purple-700" disabled={!selectedTeamId}>Crear Temporada</button>
          </div>
          <div className="mt-4">
            <h3 className="font-semibold mb-2">Lista de Temporadas</h3>
            {seasons.length === 0 ? <p className="text-sm text-gray-500">No hay temporadas creadas.</p> : (
              <ul className="space-y-2">
                {seasons.map(s => (
                  <li key={s.id} className="flex items-center justify-between p-2 bg-gray-100 rounded-lg">
                    {editingSeason?.id === s.id ? (
                      <div className="flex-1 flex gap-2">
                        <input type="text" value={editingSeason.name} onChange={(e) => setEditingSeason({ ...editingSeason, name: e.target.value })} className="flex-1 p-1 border rounded-md" />
                        <button onClick={() => editSeason(s.id, editingSeason.name)} className="text-green-600">✔</button>
                        <button onClick={() => setEditingSeason(null)} className="text-gray-500">✖</button>
                      </div>
                    ) : (
                      <>
                        <span className={`flex-1 cursor-pointer ${selectedSeasonId === s.id ? 'font-bold' : ''}`} onClick={() => setSelectedSeasonId(s.id)}>{s.name}</span>
                        <div className="flex gap-2">
                          <button onClick={() => setEditingSeason(s)} className="text-yellow-600 hover:text-yellow-700">Editar</button>
                          <button onClick={() => deleteSeason(s.id)} className="text-red-600 hover:text-red-700">Eliminar</button>
                        </div>
                      </>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  const renderMembersSection = () => (
    <>
      <div className="mb-8 border-t pt-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Agregar Miembro</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <input type="text" value={newMemberFullName} onChange={(e) => setNewMemberFullName(e.target.value)} placeholder="Nombre Completo" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" />
          <input type="date" value={newMemberDateOfBirth} onChange={(e) => setNewMemberDateOfBirth(e.target.value)} placeholder="Fecha de Nacimiento" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" />
          <select value={newMemberPosition} onChange={(e) => setNewMemberPosition(e.target.value)} className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500">
            <option value="">Seleccionar Puesto</option> {positions.map((pos, idx) => <option key={idx} value={pos}>{pos}</option>)}
          </select>
          <input type="text" value={newMemberSecondaryPosition} onChange={(e) => setNewMemberSecondaryPosition(e.target.value)} placeholder="Posición Secundaria" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" />
          <select value={newMemberDominantLeg} onChange={(e) => setNewMemberDominantLeg(e.target.value)} className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500">
            <option value="">Pierna Hábil</option> {dominantLegs.map((leg, idx) => <option key={idx} value={leg}>{leg}</option>)}
          </select>
          <input type="number" value={newMemberWeight} onChange={(e) => setNewMemberWeight(e.target.value)} placeholder="Peso (kg)" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" />
          <input type="number" value={newMemberHeight} onChange={(e) => setNewMemberHeight(e.target.value)} placeholder="Talla (cm)" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" />
          <button onClick={addMember} className="col-span-1 sm:col-span-2 bg-blue-600 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-blue-700 transition-all">Agregar</button>
        </div>
      </div>
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Miembros del Equipo</h2>
        {teamMembers.length === 0 ? (<p className="text-gray-500 text-center py-8">¡Aún no hay miembros en este equipo y temporada!</p>) : (
          <ul className="space-y-4">{teamMembers.map((member) => (
            <li key={member.id} className="bg-gray-50 p-4 rounded-lg shadow-sm border flex flex-col sm:flex-row justify-between transition-all hover:bg-gray-100">
              {editingMemberId === member.id ? (
                <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <input type="text" value={editingFullName} onChange={(e) => setEditingFullName(e.target.value)} className="p-2 border rounded-lg" />
                  <input type="date" value={editingDateOfBirth} onChange={(e) => setEditingDateOfBirth(e.target.value)} className="p-2 border rounded-lg" />
                  <select value={editingPosition} onChange={(e) => setEditingPosition(e.target.value)} className="p-2 border rounded-lg">
                    <option value="">Seleccionar Puesto</option> {positions.map((pos, idx) => <option key={idx} value={pos}>{pos}</option>)}
                  </select>
                  <input type="text" value={editingSecondaryPosition} onChange={(e) => setEditingSecondaryPosition(e.target.value)} className="p-2 border rounded-lg" />
                  <select value={editingDominantLeg} onChange={(e) => setEditingDominantLeg(e.target.value)} className="p-2 border rounded-lg">
                    <option value="">Pierna Hábil</option> {dominantLegs.map((leg, idx) => <option key={idx} value={leg}>{leg}</option>)}
                  </select>
                  <input type="number" value={editingWeight} onChange={(e) => setEditingWeight(e.target.value)} className="p-2 border rounded-lg" />
                  <input type="number" value={editingHeight} onChange={(e) => setEditingHeight(e.target.value)} className="p-2 border rounded-lg" />
                  <div className="flex gap-2 mt-2 sm:mt-0 col-span-1 sm:col-span-2 justify-end">
                    <button onClick={() => saveEditedMember(member.id)} className="bg-green-600 text-white py-2 px-4 rounded-lg shadow-md hover:bg-green-700">Guardar</button>
                    <button onClick={cancelEdit} className="bg-gray-400 text-white py-2 px-4 rounded-lg shadow-md hover:bg-gray-500">Cancelar</button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="flex-1">
                    <p className="text-lg font-bold text-gray-800">{member.fullName}</p>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-x-4 gap-y-1 mt-2 text-sm text-gray-600">
                        <p><strong>Puesto:</strong> {member.position}</p>
                        <p><strong>Nacimiento:</strong> {member.dateOfBirth}</p>
                        <p><strong>Pierna:</strong> {member.dominantLeg}</p>
                        <p><strong>Peso:</strong> {member.weight} kg</p>
                        <p><strong>Talla:</strong> {member.height} cm</p>
                        <p><strong>Secundaria:</strong> {member.secondaryPosition}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 mt-4 sm:mt-0 justify-end">
                    <button onClick={() => setViewingMember(member)} className="bg-blue-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-blue-600">Ver</button>
                    <button onClick={() => startEditing(member)} className="bg-yellow-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-yellow-600">Editar</button>
                    <button onClick={() => deleteMember(member.id)} className="bg-red-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-red-600">Eliminar</button>
                  </div>
                </>
              )}
            </li>
          ))}</ul>
        )}
      </div>
    </>
  );

  const renderTrainingsSection = () => {
    const groupedTrainings = trainingSessions.reduce((acc, training) => {
      const category = training.category || 'Sin Categoría';
      if (!acc[category]) {
        acc[category] = [];
      }
      acc[category].push(training);
      return acc;
    }, {});
  
    const sortedTrainingCategories = categories.concat('Sin Categoría').filter(cat => groupedTrainings[cat] && groupedTrainings[cat].length > 0);
  
    const handleExportTrainingsExcel = () => {
      const dataToExport = trainingSessions.map(t => {
        return {
          'Fecha': t.date,
          'Hora': t.time,
          'Lugar': t.place,
          'Categoría': t.category,
          'Sesión': t.session,
          'Macrociclo': t.macrociclo,
          'Mesociclo': t.mesociclo,
          'Microciclo': t.microciclo,
          'Objetivos': t.objectives,
          'Principios Tácticos': t.tacticalPrinciples?.map(p => `${p.name} (${p.duration} min)`).join(', ') || '',
          'Calentamiento - Descripción': t.warmup?.description,
          'Calentamiento - Duración': t.warmup?.duration,
          'Ejercicio Analítico - Descripción': t.analyticExercise?.description,
          'Ejercicio Analítico - Duración': t.analyticExercise?.duration,
          'Ejercicio Introductorio - Descripción': t.introductoryExercise?.description,
          'Ejercicio Introductorio - Duración': t.introductoryExercise?.duration,
          'Ejercicio Táctico - Descripción': t.tacticalExercise?.description,
          'Ejercicio Táctico - Duración': t.tacticalExercise?.duration,
          'ABP - Descripción': t.ABP?.description,
          'ABP - Duración': t.ABP?.duration,
          'Vuelta a la Calma - Descripción': t.cooldown?.description,
          'Vuelta a la Calma - Duración': t.cooldown?.duration,
          'Enlace Video': t.videoLinks
        };
      });
      exportToExcel(dataToExport, 'Entrenamientos');
    };

    const handleExportTrainingsWord = () => {
      if (typeof docx === 'undefined') {
        alert('La librería para exportar a Word no está cargada.');
        return;
      }
      const { Document, Packer, Paragraph, HeadingLevel, TextRun, Table, TableRow, TableCell, WidthType } = docx;

      const children = trainingSessions.flatMap(t => {
        const exerciseSection = (title, ex) => {
          if (!ex?.description) return [];
          return [
            new Paragraph({ text: title, heading: HeadingLevel.HEADING_2, spacing: { before: 200 } }),
            new Paragraph({ children: [new TextRun({ text: "Descripción: ", bold: true }), new TextRun(ex.description || '')] }),
            new Paragraph({ children: [new TextRun({ text: "Reglas: ", bold: true }), new TextRun(ex.rules || '')] }),
            new Paragraph({ children: [new TextRun({ text: "Duración: ", bold: true }), new TextRun(`${ex.duration || ''} min`)] }),
          ];
        };
        
        return [
          new Paragraph({ text: `Sesión: ${t.session || 'Sin título'} - ${t.date}`, heading: HeadingLevel.HEADING_1, spacing: { before: 300 } }),
          new Paragraph({ children: [new TextRun({ text: "Categoría: ", bold: true }), new TextRun(t.category || '')] }),
          new Paragraph({ children: [new TextRun({ text: "Objetivos: ", bold: true }), new TextRun(t.objectives || '')] }),
          ...exerciseSection('Entrada en Calor', t.warmup),
          ...exerciseSection('Ejercicio Analítico', t.analyticExercise),
          ...exerciseSection('Ejercicio Introductorio', t.introductoryExercise),
          ...exerciseSection('Ejercicio Táctico', t.tacticalExercise),
          ...exerciseSection('ABP', t.ABP),
          ...exerciseSection('Vuelta a la Calma', t.cooldown),
          new Paragraph({ text: '', spacing: { after: 400 } }),
        ];
      });

      const doc = new Document({ sections: [{ children }] });
      exportToWord(doc, 'Entrenamientos');
    };

    return (
      <>
        <div className="mb-8 border-t pt-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Generar o Añadir Entrenamiento</h2>
          <div className="bg-blue-50 p-6 rounded-lg shadow-inner mb-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Generar con Gemini ✨</h3>
            <p className="text-sm text-gray-600 mb-4">Describe los objetivos principales y la IA te sugerirá una sesión de entrenamiento completa. Puedes editar los campos antes de guardar.</p>
            <div className="space-y-4">
              <textarea
                value={generationObjectives}
                onChange={(e) => setGenerationObjectives(e.target.value)}
                placeholder="Ej: mejorar la presión alta y la transición ofensiva, ejercicios de finalización"
                className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                rows="3"
                disabled={isGenerating}
              ></textarea>
              <button
                onClick={generateTrainingWithGemini}
                className={`w-full py-3 px-6 rounded-lg font-bold transition-all ${isGenerating ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 text-white hover:bg-green-700'}`}
                disabled={isGenerating}
              >
                {isGenerating ? 'Generando...' : 'Generar Sesión con IA ✨'}
              </button>
              {generationError && <div className="text-red-500 text-sm mt-2">{generationError}</div>}
            </div>
          </div>
  
          <div className="mt-8">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Añadir Manualmente</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <input type="date" value={newTraining.date} onChange={(e) => setNewTraining({...newTraining, date: e.target.value})} placeholder="Fecha" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" />
              <input type="time" value={newTraining.time} onChange={(e) => setNewTraining({...newTraining, time: e.target.value})} placeholder="Hora" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" />
              <input type="text" value={newTraining.place} onChange={(e) => setNewTraining({...newTraining, place: e.target.value})} placeholder="Lugar" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" />
              <input type="text" value={newTraining.session} onChange={(e) => setNewTraining({...newTraining, session: e.target.value})} placeholder="Sesión" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" />
              <select value={newTraining.category} onChange={(e) => setNewTraining({...newTraining, category: e.target.value})} className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2">
                <option value="">Seleccionar Categoría</option>
                {categories.map((cat) => (<option key={cat} value={cat}>{cat}</option>))}
              </select>
              <input type="text" value={newTraining.macrociclo} onChange={(e) => setNewTraining({...newTraining, macrociclo: e.target.value})} placeholder="Macrociclo" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" />
              <input type="text" value={newTraining.mesociclo} onChange={(e) => setNewTraining({...newTraining, mesociclo: e.target.value})} placeholder="Mesociclo" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" />
              <input type="text" value={newTraining.microciclo} onChange={(e) => setNewTraining({...newTraining, microciclo: e.target.value})} placeholder="Microciclo" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" />
              <textarea value={newTraining.objectives} onChange={(e) => setNewTraining({...newTraining, objectives: e.target.value})} placeholder="Objetivos" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" rows="3"></textarea>
              {['warmup', 'analyticExercise', 'introductoryExercise', 'tacticalExercise', 'ABP', 'cooldown'].map((exerciseType) => (
                <div key={exerciseType} className="col-span-1 sm:col-span-2 border rounded-lg p-4 bg-gray-50 mb-4">
                  <h3 className="font-semibold text-lg mb-2">{
                    exerciseType === 'warmup' ? 'Entrada en Calor' :
                    exerciseType === 'analyticExercise' ? 'Ejercicio Analítico Táctico Colectivo' :
                    exerciseType === 'introductoryExercise' ? 'Ejercicio Introductorio' :
                    exerciseType === 'tacticalExercise' ? 'Ejercicio Táctico' :
                    exerciseType === 'ABP' ? 'ABP' : 'Vuelta a la Calma'
                  }</h3>
                  <textarea value={newTraining[exerciseType].description} onChange={(e) => handleExerciseChange(exerciseType, 'description', e.target.value)} placeholder="Descripción del ejercicio" className="w-full p-2 border rounded-lg mb-2"></textarea>
                  <input type="text" value={newTraining[exerciseType].rules} onChange={(e) => handleExerciseChange(exerciseType, 'rules', e.target.value)} placeholder="Reglas de provocación" className="w-full p-2 border rounded-lg mb-2" />
                  <input type="text" value={newTraining[exerciseType].coachMessage} onChange={(e) => handleExerciseChange(exerciseType, 'coachMessage', e.target.value)} placeholder="Mensaje del entrenador" className="w-full p-2 border rounded-lg mb-2" />
                  <input type="text" value={newTraining[exerciseType].space} onChange={(e) => handleExerciseChange(exerciseType, 'space', e.target.value)} placeholder="Dimensiones del espacio (Ej: 20x30m)" className="w-full p-2 border rounded-lg mb-2" />
                  <input type="number" value={newTraining[exerciseType].duration} onChange={(e) => handleExerciseChange(exerciseType, 'duration', e.target.value)} placeholder="Duración (min)" className="w-full p-2 border rounded-lg mb-2" />
                  <input type="number" value={newTraining[exerciseType].series} onChange={(e) => handleExerciseChange(exerciseType, 'series', e.target.value)} placeholder="Series" className="w-full p-2 border rounded-lg mb-2" />
                  <input type="number" value={newTraining[exerciseType].rest} onChange={(e) => handleExerciseChange(exerciseType, 'rest', e.target.value)} placeholder="Descanso entre series (min)" className="w-full p-2 border rounded-lg" />
                </div>
              ))}
              <div className="col-span-1 sm:col-span-2 border rounded-lg p-4 bg-yellow-50 mb-4">
                <h3 className="font-semibold text-lg mb-2">Principios Tácticos</h3>
                {newTraining.tacticalPrinciples.map((principle, index) => (
                  <div key={index} className="flex gap-2 mb-2 items-center">
                    <select value={principle.name} onChange={(e) => handleTacticalPrincipleChange(index, 'name', e.target.value)} className="flex-1 p-2 border rounded-lg">
                      <option value="">Seleccionar Principio</option>
                      {tacticalPrinciples.map(p => <option key={p.id} value={p.name}>{p.name}</option>)}
                    </select>
                    <input type="number" value={principle.duration} onChange={(e) => handleTacticalPrincipleChange(index, 'duration', e.target.value)} placeholder="Duración (min)" className="w-24 p-2 border rounded-lg" />
                  </div>
                ))}
                <button onClick={addTacticalPrincipleToTraining} className="mt-2 bg-blue-500 text-white font-bold py-2 px-4 rounded-lg shadow-md hover:bg-blue-600 transition-all w-full">Añadir Principio Táctico</button>
              </div>
              <input type="text" value={newTraining.coachesRoles} onChange={(e) => setNewTraining({...newTraining, coachesRoles: e.target.value})} placeholder="Roles de los entrenadores" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" />
              <input type="text" value={newTraining.totalVolume} onChange={(e) => setNewTraining({...newTraining, totalVolume: e.target.value})} placeholder="Volumen total de la sesión" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" />
              <input type="url" value={newTraining.photoLinks} onChange={(e) => setNewTraining({...newTraining, photoLinks: e.target.value})} placeholder="Enlaces de fotos" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" />
              <input type="url" value={newTraining.videoLinks} onChange={(e) => setNewTraining({...newTraining, videoLinks: e.target.value})} placeholder="Enlaces de videos" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" />
              <button onClick={editingTrainingId ? () => saveEditedTraining(editingTrainingId) : addTraining} className="col-span-1 sm:col-span-2 bg-green-600 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-green-700 transition-all">
                {editingTrainingId ? 'Guardar Cambios' : 'Agregar Entrenamiento'}
              </button>
              {editingTrainingId && <button onClick={cancelTrainingEdit} className="col-span-1 sm:col-span-2 bg-gray-400 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-gray-500">Cancelar</button>}
            </div>
          </div>
        </div>
        <div>
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Entrenamientos</h2>
          {trainingSessions.length === 0 ? (
            <p className="text-gray-500 text-center py-8">¡Aún no hay entrenamientos en esta temporada!</p>
          ) : (
            <>
            <div className="space-y-8">
              {sortedTrainingCategories.map(category => (
                <div key={category} className="bg-gray-100 p-6 rounded-xl shadow-lg border">
                  <h3 className="text-2xl font-bold text-gray-800 mb-4">{category}</h3>
                  <ul className="space-y-4">
                    {groupedTrainings[category].map(training => (
                      <li key={training.id} className="bg-white p-4 rounded-lg shadow-sm border flex flex-col justify-between transition-all hover:bg-gray-50">
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                          <div className="text-lg font-bold text-gray-800 col-span-full">Sesión: {training.session || 'N/A'}</div>
                          <div className="text-gray-500">Fecha: <span className="font-semibold">{training.date}</span></div>
                          <div className="text-gray-500">Hora: <span className="font-semibold">{training.time}</span></div>
                          <div className="text-gray-500">Lugar: <span className="font-semibold">{training.place}</span></div>
                          <div className="text-gray-500">Macrociclo: <span className="font-semibold">{training.macrociclo || 'N/A'}</span></div>
                          <div className="text-gray-500">Mesociclo: <span className="font-semibold">{training.mesociclo || 'N/A'}</span></div>
                          <div className="text-gray-500">Microciclo: <span className="font-semibold">{training.microciclo || 'N/A'}</span></div>
                          {training.tacticalPrinciples && training.tacticalPrinciples.length > 0 && (
                            <div className="col-span-full mt-2">
                              <p className="font-semibold text-gray-800">Principios Tácticos:</p>
                              <ul className="list-disc list-inside text-sm text-gray-600">
                                {training.tacticalPrinciples.map((p, idx) => (
                                  <li key={idx}>{p.name}: {p.duration} min</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                        <div className="flex items-center gap-2 mt-4 justify-end">
                          <button onClick={() => setViewingTraining(training)} className="bg-blue-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-blue-600">Ver</button>
                          <button onClick={() => startEditingTraining(training)} className="bg-yellow-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-yellow-600">Editar</button>
                          <button onClick={() => deleteTraining(training.id)} className="bg-red-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-red-600">Eliminar</button>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
            <div className="mt-8 border-t pt-6 text-center">
              <h3 className="text-lg font-semibold text-gray-700 mb-4">Opciones de Exportación</h3>
              <div className="flex justify-center gap-4">
                <button onClick={handleExportTrainingsExcel} className="bg-green-600 text-white font-bold py-2 px-4 rounded-lg shadow-md hover:bg-green-700">Exportar a Excel</button>
                <button onClick={handleExportTrainingsWord} className="bg-blue-600 text-white font-bold py-2 px-4 rounded-lg shadow-md hover:bg-blue-700">Exportar a Word</button>
              </div>
            </div>
            </>
          )}
        </div>
      </>
    );
  };

  const renderAttendanceSection = () => {
    const handleExportAttendanceExcel = () => {
      const dataToExport = teamMembers.map(member => {
        const memberAttendance = attendance[member.fullName];
        return {
          'Jugador': member.fullName,
          'Fecha': todayDate,
          'Estado': memberAttendance?.status || 'No marcado',
          'Justificación': memberAttendance?.justification || '',
        };
      });
      exportToExcel(dataToExport, `Asistencia_${todayDate}`);
    };

    const handleExportAttendanceWord = () => {
      if (typeof docx === 'undefined') return;
      const { Document, Packer, Paragraph, HeadingLevel, Table, TableRow, TableCell } = docx;

      const rows = [
        new TableRow({ children: [
          new TableCell({ children: [new Paragraph({ text: "Jugador", style: "strong" })] }),
          new TableCell({ children: [new Paragraph({ text: "Estado", style: "strong" })] }),
          new TableCell({ children: [new Paragraph({ text: "Justificación", style: "strong" })] }),
        ]}),
        ...teamMembers.map(member => {
          const memberAttendance = attendance[member.fullName];
          return new TableRow({ children: [
            new TableCell({ children: [new Paragraph(member.fullName)] }),
            new TableCell({ children: [new Paragraph(memberAttendance?.status || 'No marcado')] }),
            new TableCell({ children: [new Paragraph(memberAttendance?.justification || '')] }),
          ]});
        })
      ];

      const table = new Table({ rows });
      const doc = new Document({
        sections: [{
          children: [
            new Paragraph({ text: `Informe de Asistencia - ${todayDate}`, heading: HeadingLevel.HEADING_1 }),
            table,
          ],
        }],
      });
      exportToWord(doc, `Asistencia_${todayDate}`);
    };
    
    return (
    <>
      <div className="mb-8 border-t pt-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Asistencia Diaria ({todayDate})</h2>
        {teamMembers.length === 0 ? (<p className="text-gray-500 text-center py-8">¡Añade jugadores para registrar la asistencia!</p>) : (
          <>
          <ul className="space-y-4">{teamMembers.map((member) => {
            const memberAttendance = attendance[member.fullName];
            const status = memberAttendance?.status || 'No marcado';
            const justification = memberAttendance?.justification;
            return (
              <li key={member.id} className="p-4 bg-gray-50 rounded-lg shadow-sm border flex flex-col sm:flex-row items-center justify-between">
                <div className="flex-1 min-w-0 mb-2 sm:mb-0">
                  <p className="font-bold text-gray-800">{member.fullName}</p>
                  <p className="text-sm text-gray-500">Estado:
                    <span className={`ml-2 px-2 py-1 rounded-full text-xs font-semibold
                      ${status === 'Presente' ? 'bg-green-100 text-green-800' : status === 'Ausente' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`
                    }>
                      {status}
                    </span>
                  </p>
                  {justification && <p className="text-sm text-gray-500 mt-1">Justificación: <span className="font-semibold">{justification}</span></p>}
                </div>
                <div className="flex gap-2">
                  <button onClick={() => markAttendance(member.fullName, 'Presente')} className={`px-4 py-2 rounded-lg text-white font-semibold transition-colors
                      ${status === 'Presente' ? 'bg-green-600 opacity-50 cursor-not-allowed' : 'bg-green-500 hover:bg-green-600'}`} disabled={status === 'Presente'}>Presente</button>
                  <select onChange={(e) => justifyAbsence(member.fullName, e.target.value)} value={justification || ''}
                    className={`px-4 py-2 rounded-lg text-sm bg-red-500 text-white font-semibold cursor-pointer transition-all
                      ${status !== 'Ausente' ? 'hidden' : ''}`}>
                    <option value="" disabled>Justificar...</option> {justifications.map((just, idx) => <option key={idx} value={just}>{just}</option>)}
                  </select>
                  <button onClick={() => markAttendance(member.fullName, 'Ausente')} className={`px-4 py-2 rounded-lg text-white font-semibold transition-colors
                      ${status === 'Ausente' ? 'bg-red-600 opacity-50 cursor-not-allowed' : 'bg-red-500 hover:bg-red-600'}
                      ${status === 'Ausente' ? 'hidden' : ''}`} disabled={status === 'Ausente'}>Ausente</button>
                </div>
              </li>
            );
          })}</ul>
           <div className="mt-8 border-t pt-6 text-center">
              <h3 className="text-lg font-semibold text-gray-700 mb-4">Opciones de Exportación</h3>
              <div className="flex justify-center gap-4">
                <button onClick={handleExportAttendanceExcel} className="bg-green-600 text-white font-bold py-2 px-4 rounded-lg shadow-md hover:bg-green-700">Exportar a Excel</button>
                <button onClick={handleExportAttendanceWord} className="bg-blue-600 text-white font-bold py-2 px-4 rounded-lg shadow-md hover:bg-blue-700">Exportar a Word</button>
              </div>
            </div>
          </>
        )}
      </div>
    </>
  )};

  const renderTacticalPrinciplesSection = () => {
    // Calculate total minutes per principle
    const principlesSummary = trainingSessions.reduce((acc, training) => {
      if (training.tacticalPrinciples) {
        training.tacticalPrinciples.forEach(p => {
          const name = p.name;
          const duration = parseInt(p.duration, 10) || 0;
          if (acc[name]) {
            acc[name] += duration;
          } else {
            acc[name] = duration;
          }
        });
      }
      return acc;
    }, {});

    return (
      <>
        <div className="mb-8 border-t pt-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Agregar Principio Táctico</h2>
          <div className="flex gap-2">
            <input type="text" value={newPrincipleName} onChange={(e) => setNewPrincipleName(e.target.value)} placeholder="Ej: Salida de balón" className="flex-1 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" />
            <button onClick={addPrinciple} className="bg-blue-600 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-blue-700">Agregar</button>
          </div>
        </div>
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Principios Tácticos y Tiempo de Trabajo</h2>
          {tacticalPrinciples.length === 0 ? (<p className="text-gray-500 text-center py-8">¡Aún no hay principios tácticos registrados!</p>) : (
            <ul className="space-y-4">
              {tacticalPrinciples.map((principle) => (
                <li key={principle.id} className="bg-gray-50 p-4 rounded-lg shadow-sm border flex flex-col sm:flex-row justify-between items-center transition-all hover:bg-gray-100">
                  {editingPrincipleId === principle.id ? (
                    <div className="flex-1 flex gap-2 w-full">
                      <input type="text" value={editingPrincipleName} onChange={(e) => setEditingPrincipleName(e.target.value)} className="flex-1 p-2 border rounded-lg" />
                      <div className="flex gap-2">
                        <button onClick={() => saveEditedPrinciple(principle.id)} className="bg-green-600 text-white py-2 px-4 rounded-lg shadow-md hover:bg-green-700">Guardar</button>
                        <button onClick={cancelPrincipleEdit} className="bg-gray-400 text-white py-2 px-4 rounded-lg shadow-md hover:bg-gray-500">Cancelar</button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="flex-1">
                        <div className="text-lg font-bold text-gray-800">{principle.name}</div>
                        <div className="text-sm text-gray-500 mt-1">Tiempo total: <span className="font-semibold text-gray-800">{formatMinutes(principlesSummary[principle.name] || 0)}</span></div>
                        <button onClick={() => explainPrinciple(principle.name)} className="mt-2 text-sm text-blue-600 hover:text-blue-700 hover:underline transition-colors">
                          Explicar con IA ✨
                        </button>
                      </div>
                      <div className="flex gap-2 mt-2 sm:mt-0">
                        <button onClick={() => startEditingPrinciple(principle)} className="bg-yellow-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-yellow-600">Editar</button>
                        <button onClick={() => deletePrinciple(principle.id)} className="bg-red-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-red-600">Eliminar</button>
                      </div>
                    </>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
        {principleExplanation && (
          <div className="mt-8 p-6 bg-blue-100 rounded-lg shadow-lg">
            <h3 className="text-xl font-bold text-blue-800 mb-2">Explicación del Principio Táctico</h3>
            <p className="text-gray-800 whitespace-pre-wrap">{principleExplanation}</p>
          </div>
        )}
        {isExplainingPrinciple && (
            <div className="text-center text-gray-500 mt-4">Obteniendo explicación...</div>
        )}
      </>
    );
  };

  const renderVideosSection = () => (
    <>
      <div className="mb-8 border-t pt-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Videos de Entrenamiento</h2>
        <div className="flex justify-center mb-6">
            <button
                onClick={() => setActiveVideoSection('mis_entrenamientos')}
                className={`py-2 px-4 rounded-l-full font-bold transition-all duration-300 ${activeVideoSection === 'mis_entrenamientos' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}
            >
                Mis Entrenamientos
            </button>
            <button
                onClick={() => setActiveVideoSection('otros_entrenamientos')}
                className={`py-2 px-4 rounded-r-full font-bold transition-all duration-300 ${activeVideoSection === 'otros_entrenamientos' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}
            >
                De Otros Entrenadores
            </button>
        </div>
        <div className="bg-gray-50 p-6 rounded-xl shadow-lg mb-8">
            <h3 className="text-xl font-bold mb-4 text-center">{editingVideo ? 'Editar Video' : 'Añadir Nuevo Video'}</h3>
            <form onSubmit={editingVideo ? saveEditedVideo : addVideo} className="space-y-4">
                <div>
                    <label className="block text-gray-600 mb-1">Nombre del Ejercicio</label>
                    <input
                        type="text"
                        name="name"
                        value={editingVideo ? editingVideo.name : newVideo.name}
                        onChange={handleVideoInputChange}
                        placeholder="Ej: Ejercicio de 1 vs 1"
                        className="w-full p-3 rounded-lg bg-white text-gray-800 border focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
                <div>
                    <label className="block text-gray-600 mb-1">Enlace del Video</label>
                    <input
                        type="url"
                        name="url"
                        value={editingVideo ? editingVideo.url : newVideo.url}
                        onChange={handleVideoInputChange}
                        placeholder="https://www.youtube.com/watch?v=ejemplo"
                        className="w-full p-3 rounded-lg bg-white text-gray-800 border focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
                <div>
                    <label className="block text-gray-600 mb-1">Categoría</label>
                    <select
                        name="category"
                        value={editingVideo ? editingVideo.category : newVideo.category}
                        onChange={handleVideoInputChange}
                        className="w-full p-3 rounded-lg bg-white text-gray-800 border focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="">Selecciona una categoría</option>
                        {categories.map(cat => (
                            <option key={cat} value={cat}>{cat}</option>
                        ))}
                    </select>
                </div>
                <div className="flex gap-2">
                  <button
                      type="submit"
                      className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-all duration-300 shadow-lg"
                  >
                      {editingVideo ? 'Guardar Cambios' : 'Guardar Video'}
                  </button>
                  {editingVideo && (
                    <button
                        type="button"
                        onClick={cancelVideoEdit}
                        className="bg-gray-400 hover:bg-gray-500 text-white font-bold py-3 px-6 rounded-lg transition-all duration-300"
                    >
                        Cancelar
                    </button>
                  )}
                </div>
            </form>
            {videoMessage && (
                <div className="mt-4 text-center text-sm font-semibold text-blue-600">
                    {videoMessage}
                </div>
            )}
        </div>
        <div>
            <h3 className="text-xl md:text-2xl font-bold text-center text-gray-800 mb-6">
                {activeVideoSection === 'mis_entrenamientos' ? 'Mis Videos' : 'Videos de Otros Entrenadores'}
            </h3>
            {isLoadingVideos ? (
                <div className="text-center text-gray-500">
                    Cargando videos...
                </div>
            ) : (
                <VideoList videos={activeVideoSection === 'mis_entrenamientos' ? myTrainings : otherTrainings} />
            )}
        </div>
      </div>
    </>
  );

  const renderMatchPlansSection = () => {
    const handleExportMatchPlansExcel = () => {
      const dataToExport = matchPlans.map(p => ({
        'Rival': p.rival,
        'Fecha': p.date,
        'Lugar': p.place,
        'Hora': p.time,
        'Fortalezas Rival': p.rivalStrengths,
        'Debilidades Rival': p.rivalWeaknesses,
        'Org. Ofensiva': p.offensiveOrganization,
        'Org. Defensiva': p.defensiveOrganization,
        'Trans. Ofensiva': p.offensiveTransition,
        'Trans. Defensiva': p.defensiveTransition,
        'ABP Ofensivo': p.offensiveABP,
        'ABP Defensivo': p.defensiveABP,
        'Notas Adicionales': p.additionalNotes,
        'Enlace Video': p.videoLink,
      }));
      exportToExcel(dataToExport, 'Planes_de_Partido');
    };

    const handleExportMatchPlansWord = () => {
      if (typeof docx === 'undefined') return;
      const { Document, Packer, Paragraph, HeadingLevel, TextRun } = docx;

      const children = matchPlans.flatMap(p => [
        new Paragraph({ text: `Plan de Partido vs ${p.rival}`, heading: HeadingLevel.HEADING_1, spacing: { before: 300 } }),
        new Paragraph({ children: [new TextRun({ text: "Fecha: ", bold: true }), new TextRun(p.date || '')] }),
        new Paragraph({ text: "Análisis del Rival", heading: HeadingLevel.HEADING_2, spacing: { before: 200 } }),
        new Paragraph({ children: [new TextRun({ text: "Fortalezas: ", bold: true }), new TextRun(p.rivalStrengths || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Debilidades: ", bold: true }), new TextRun(p.rivalWeaknesses || '')] }),
        new Paragraph({ text: "Momentos del Juego", heading: HeadingLevel.HEADING_2, spacing: { before: 200 } }),
        new Paragraph({ children: [new TextRun({ text: "Organización Ofensiva: ", bold: true }), new TextRun(p.offensiveOrganization || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Organización Defensiva: ", bold: true }), new TextRun(p.defensiveOrganization || '')] }),
        new Paragraph({ text: '', spacing: { after: 400 } }),
      ]);

      const doc = new Document({ sections: [{ children }] });
      exportToWord(doc, 'Planes_de_Partido');
    };
    
    return (
    <>
      <div className="mb-8 border-t pt-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Añadir Plan de Partido</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <input type="text" name="rival" value={newMatchPlan.rival} onChange={handleMatchPlanChange} placeholder="Rival" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" />
          <input type="date" name="date" value={newMatchPlan.date} onChange={handleMatchPlanChange} placeholder="Fecha" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" />
          <input type="text" name="place" value={newMatchPlan.place} onChange={handleMatchPlanChange} placeholder="Lugar" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" />
          <input type="time" name="time" value={newMatchPlan.time} onChange={handleMatchPlanChange} placeholder="Hora" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" />
          
          <textarea name="rivalStrengths" value={newMatchPlan.rivalStrengths} onChange={handleMatchPlanChange} placeholder="Fortalezas del Rival" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" rows="3"></textarea>
          <textarea name="rivalWeaknesses" value={newMatchPlan.rivalWeaknesses} onChange={handleMatchPlanChange} placeholder="Debilidades del Rival" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" rows="3"></textarea>

          <h3 className="text-lg font-semibold text-gray-800 col-span-full mt-4">Momentos del Juego</h3>
          <textarea name="offensiveOrganization" value={newMatchPlan.offensiveOrganization} onChange={handleMatchPlanChange} placeholder="Organización Ofensiva" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" rows="3"></textarea>
          <textarea name="defensiveOrganization" value={newMatchPlan.defensiveOrganization} onChange={handleMatchPlanChange} placeholder="Organización Defensiva" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" rows="3"></textarea>
          <textarea name="offensiveTransition" value={newMatchPlan.offensiveTransition} onChange={handleMatchPlanChange} placeholder="Transición Ofensiva" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" rows="3"></textarea>
          <textarea name="defensiveTransition" value={newMatchPlan.defensiveTransition} onChange={handleMatchPlanChange} placeholder="Transición Defensiva" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" rows="3"></textarea>
          <textarea name="offensiveABP" value={newMatchPlan.offensiveABP} onChange={handleMatchPlanChange} placeholder="ABP Ofensivo" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" rows="3"></textarea>
          <textarea name="defensiveABP" value={newMatchPlan.defensiveABP} onChange={handleMatchPlanChange} placeholder="ABP Defensivo" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" rows="3"></textarea>
          
          <textarea name="additionalNotes" value={newMatchPlan.additionalNotes} onChange={handleMatchPlanChange} placeholder="Notas Adicionales" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" rows="3"></textarea>
          <input type="url" name="videoLink" value={newMatchPlan.videoLink} onChange={handleMatchPlanChange} placeholder="Enlace de Video del Partido" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" />
          
          <button onClick={editingMatchPlanId ? () => saveEditedMatchPlan(editingMatchPlanId) : addMatchPlan} className="col-span-1 sm:col-span-2 bg-green-600 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-green-700 transition-all">
            {editingMatchPlanId ? 'Guardar Cambios' : 'Añadir Plan de Partido'}
          </button>
          {editingMatchPlanId && <button onClick={cancelMatchPlanEdit} className="col-span-1 sm:col-span-2 bg-gray-400 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-gray-500">Cancelar</button>}
        </div>
      </div>
      <div>
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Planes de Partidos</h2>
        {matchPlans.length === 0 ? (<p className="text-gray-500 text-center py-8">¡Aún no hay planes de partidos en esta temporada!</p>) : (
          <>
          <ul className="space-y-4">{matchPlans.map((plan) => (
            <li key={plan.id} className="bg-gray-50 p-4 rounded-lg shadow-sm border flex flex-col justify-between transition-all hover:bg-gray-100">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                <div className="text-lg font-bold text-gray-800">Rival: {plan.rival}</div>
                <div className="text-gray-500">Fecha: <span className="font-semibold">{plan.date}</span></div>
                <div className="text-gray-500">Hora: <span className="font-semibold">{plan.time}</span></div>
                <div className="text-gray-500">Lugar: <span className="font-semibold">{plan.place}</span></div>
                {plan.videoLink && (
                  <div className="col-span-full text-center mt-2">
                    <a href={plan.videoLink} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-500 transition-colors duration-200 text-sm font-semibold">Ver Video del Partido</a>
                  </div>
                )}
              </div>
              <div className="mt-4 border-t pt-4">
                <p className="font-semibold text-gray-800">Fortalezas del Rival:</p>
                <p className="text-gray-600 whitespace-pre-wrap">{plan.rivalStrengths}</p>
                <p className="font-semibold text-gray-800 mt-2">Debilidades del Rival:</p>
                <p className="text-gray-600 whitespace-pre-wrap">{plan.rivalWeaknesses}</p>
              </div>
              <div className="mt-4 border-t pt-4">
                <p className="font-semibold text-gray-800">Momentos del Juego:</p>
                <ul className="list-disc list-inside text-sm text-gray-600 space-y-2 mt-2">
                  <li><span className="font-semibold">Organización Ofensiva:</span> {plan.offensiveOrganization}</li>
                  <li><span className="font-semibold">Organización Defensiva:</span> {plan.defensiveOrganization}</li>
                  <li><span className="font-semibold">Transición Ofensiva:</span> {plan.offensiveTransition}</li>
                  <li><span className="font-semibold">Transición Defensiva:</span> {plan.defensiveTransition}</li>
                  <li><span className="font-semibold">ABP Ofensivo:</span> {plan.offensiveABP}</li>
                  <li><span className="font-semibold">ABP Defensivo:</span> {plan.defensiveABP}</li>
                </ul>
              </div>
              <div className="mt-4 border-t pt-4">
                <p className="font-semibold text-gray-800">Notas Adicionales:</p>
                <p className="text-gray-600 whitespace-pre-wrap">{plan.additionalNotes}</p>
              </div>
              <div className="flex items-center gap-2 mt-4 justify-end">
                <button onClick={() => startEditingMatchPlan(plan)} className="bg-yellow-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-yellow-600">Editar</button>
                <button onClick={() => deleteMatchPlan(plan.id)} className="bg-red-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-red-600">Eliminar</button>
              </div>
            </li>
          ))}</ul>
          <div className="mt-8 border-t pt-6 text-center">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">Opciones de Exportación</h3>
            <div className="flex justify-center gap-4">
              <button onClick={handleExportMatchPlansExcel} className="bg-green-600 text-white font-bold py-2 px-4 rounded-lg shadow-md hover:bg-green-700">Exportar a Excel</button>
              <button onClick={handleExportMatchPlansWord} className="bg-blue-600 text-white font-bold py-2 px-4 rounded-lg shadow-md hover:bg-blue-700">Exportar a Word</button>
            </div>
          </div>
          </>
        )}
      </div>
    </>
  )};

  const renderVideoAnalysisSection = () => {
    const handleExportAnalysisExcel = () => {
      const dataToExport = videoAnalyses[activeAnalysisSection].map(a => ({
        'Equipo Analizado': a.equipoAnalizado,
        'Rival': a.rival,
        'Lugar': a.lugar,
        'Fecha Informe': a.fechaInforme,
        'Sistema de Juego': a.sistemaJuego,
        'Org. Ofensiva - Inicio': a.organizacionOfensiva?.inicio,
        'Org. Ofensiva - Creación': a.organizacionOfensiva?.creacion,
        'Org. Ofensiva - Finalización': a.organizacionOfensiva?.finalizacion,
        'Org. Defensiva': a.organizacionDefensiva,
        'Trans. Ofensiva': a.transicionOfensiva,
        'Trans. Defensiva': a.transicionDefensiva,
        'ABP Ofensivo': a.abpOfensivo,
        'ABP Defensivo': a.abpDefensivo,
        'Laterales': a.laterales,
        'Fortalezas': a.fortalezas,
        'Debilidades': a.debilidades,
        'Notas Adicionales': a.notasAdicionales,
        'Enlace Video': a.enlaceVideo,
      }));
      exportToExcel(dataToExport, `Video_Analisis_${activeAnalysisSection}`);
    };

    const handleExportAnalysisWord = () => {
      if (typeof docx === 'undefined') return;
      const { Document, Packer, Paragraph, HeadingLevel, TextRun } = docx;

      const children = videoAnalyses[activeAnalysisSection].flatMap(a => [
        new Paragraph({ text: `Análisis: ${a.equipoAnalizado} vs ${a.rival}`, heading: HeadingLevel.HEADING_1, spacing: { before: 300 } }),
        new Paragraph({ children: [new TextRun({ text: "Fecha Informe: ", bold: true }), new TextRun(a.fechaInforme || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Sistema de Juego: ", bold: true }), new TextRun(a.sistemaJuego || '')] }),
        new Paragraph({ text: "Momentos del Juego", heading: HeadingLevel.HEADING_2, spacing: { before: 200 } }),
        new Paragraph({ children: [new TextRun({ text: "Fortalezas: ", bold: true }), new TextRun(a.fortalezas || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Debilidades: ", bold: true }), new TextRun(a.debilidades || '')] }),
        new Paragraph({ text: '', spacing: { after: 400 } }),
      ]);
      const doc = new Document({ sections: [{ children }] });
      exportToWord(doc, `Video_Analisis_${activeAnalysisSection}`);
    };
    
    return (
    <>
      <div className="mb-8 border-t pt-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Análisis de Video</h2>
        <div className="flex justify-center mb-6">
          <button
            onClick={() => setActiveAnalysisSection('myTeam')}
            className={`py-2 px-4 rounded-l-full font-bold transition-all duration-300 ${activeAnalysisSection === 'myTeam' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}
          >
            Mi Equipo
          </button>
          <button
            onClick={() => setActiveAnalysisSection('rivalTeam')}
            className={`py-2 px-4 rounded-r-full font-bold transition-all duration-300 ${activeAnalysisSection === 'rivalTeam' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}
          >
            Equipo Rival
          </button>
        </div>
        
        <div className="bg-gray-50 p-6 rounded-xl shadow-lg mb-8">
            <h3 className="text-xl font-bold mb-4 text-center">{editingAnalysisId ? 'Editar Análisis' : 'Añadir Nuevo Análisis'}</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <input type="text" name="equipoAnalizado" value={newAnalysis.equipoAnalizado} onChange={handleAnalysisChange} placeholder="Equipo Analizado" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"/>
                <input type="text" name="rival" value={newAnalysis.rival} onChange={handleAnalysisChange} placeholder="Rival" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"/>
                <input type="text" name="lugar" value={newAnalysis.lugar} onChange={handleAnalysisChange} placeholder="Lugar del Partido" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"/>
                <input type="date" name="fechaInforme" value={newAnalysis.fechaInforme} onChange={handleAnalysisChange} placeholder="Fecha del Informe" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"/>
                
                <input type="text" name="sistemaJuego" value={newAnalysis.sistemaJuego} onChange={handleAnalysisChange} placeholder="Sistema de Juego (Ej: 4-3-3)" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2"/>

                <div className="col-span-1 sm:col-span-2 border-t pt-4 mt-4">
                  <h4 className="text-lg font-semibold text-gray-700 mb-2">Momentos del Juego</h4>
                  <div className="bg-white p-4 rounded-lg border">
                    <h5 className="font-semibold mb-2">Organización Ofensiva</h5>
                    <textarea name="inicio" value={newAnalysis.organizacionOfensiva.inicio} onChange={(e) => handleNestedAnalysisChange('organizacionOfensiva', 'inicio', e.target.value)} placeholder="Inicio" className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 mb-2" rows="2"></textarea>
                    <textarea name="creacion" value={newAnalysis.organizacionOfensiva.creacion} onChange={(e) => handleNestedAnalysisChange('organizacionOfensiva', 'creacion', e.target.value)} placeholder="Creación y Progresión" className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 mb-2" rows="2"></textarea>
                    <textarea name="finalizacion" value={newAnalysis.organizacionOfensiva.finalizacion} onChange={(e) => handleNestedAnalysisChange('organizacionOfensiva', 'finalizacion', e.target.value)} placeholder="Finalización" className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" rows="2"></textarea>
                  </div>
                  <textarea name="organizacionDefensiva" value={newAnalysis.organizacionDefensiva} onChange={handleAnalysisChange} placeholder="Organización Defensiva" className="mt-2 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2 w-full" rows="3"></textarea>
                  <textarea name="transicionOfensiva" value={newAnalysis.transicionOfensiva} onChange={handleAnalysisChange} placeholder="Transición Ofensiva" className="mt-2 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2 w-full" rows="3"></textarea>
                  <textarea name="transicionDefensiva" value={newAnalysis.transicionDefensiva} onChange={handleAnalysisChange} placeholder="Transición Defensiva" className="mt-2 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2 w-full" rows="3"></textarea>
                  <textarea name="abpOfensivo" value={newAnalysis.abpOfensivo} onChange={handleAnalysisChange} placeholder="ABP Ofensivo" className="mt-2 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2 w-full" rows="3"></textarea>
                  <textarea name="abpDefensivo" value={newAnalysis.abpDefensivo} onChange={handleAnalysisChange} placeholder="ABP Defensivo" className="mt-2 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2 w-full" rows="3"></textarea>
                  <textarea name="laterales" value={newAnalysis.laterales} onChange={handleAnalysisChange} placeholder="Laterales" className="mt-2 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2 w-full" rows="3"></textarea>
                </div>

                <textarea name="fortalezas" value={newAnalysis.fortalezas} onChange={handleAnalysisChange} placeholder="Fortalezas" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" rows="3"></textarea>
                <textarea name="debilidades" value={newAnalysis.debilidades} onChange={handleAnalysisChange} placeholder="Debilidades" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" rows="3"></textarea>
                
                <textarea name="notasAdicionales" value={newAnalysis.notasAdicionales} onChange={handleAnalysisChange} placeholder="Notas Adicionales" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" rows="3"></textarea>
                <input type="url" name="enlaceVideo" value={newAnalysis.enlaceVideo} onChange={handleAnalysisChange} placeholder="Enlace de Video" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2"/>
                <div className="col-span-1 sm:col-span-2 flex gap-2">
                  <button onClick={addOrUpdateAnalysis} className="flex-1 bg-green-600 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-green-700 transition-all">
                    {editingAnalysisId ? 'Guardar Cambios' : 'Guardar Análisis'}
                  </button>
                  {editingAnalysisId && (
                    <button onClick={cancelEditingAnalysis} className="bg-gray-400 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-gray-500">
                      Cancelar
                    </button>
                  )}
                </div>
            </div>
        </div>

        <div>
            <h3 className="text-xl md:text-2xl font-bold text-center text-gray-800 mb-6">
              Análisis Guardados: {activeAnalysisSection === 'myTeam' ? 'Mi Equipo' : 'Equipo Rival'}
            </h3>
            <ul className="space-y-4">
              {videoAnalyses[activeAnalysisSection].map(analysis => (
                <li key={analysis.id} className="bg-white p-4 rounded-lg shadow-sm border">
                  <div className="flex flex-col sm:flex-row justify-between">
                    <div className="flex-1">
                      <p className="font-bold text-lg">{analysis.equipoAnalizado} vs {analysis.rival}</p>
                      <p className="text-sm text-gray-500">{analysis.fechaInforme}</p>
                    </div>
                    <div className="flex items-center gap-2 mt-4 sm:mt-0 justify-end">
                      <button onClick={() => setViewingAnalysis(analysis)} className="bg-blue-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-blue-600">Ver</button>
                      <button onClick={() => startEditingAnalysis(analysis)} className="bg-yellow-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-yellow-600">Editar</button>
                      <button onClick={() => deleteAnalysis(analysis.id)} className="bg-red-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-red-600">Eliminar</button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
             <div className="mt-8 border-t pt-6 text-center">
              <h3 className="text-lg font-semibold text-gray-700 mb-4">Opciones de Exportación</h3>
              <div className="flex justify-center gap-4">
                <button onClick={handleExportAnalysisExcel} className="bg-green-600 text-white font-bold py-2 px-4 rounded-lg shadow-md hover:bg-green-700">Exportar a Excel</button>
                <button onClick={handleExportAnalysisWord} className="bg-blue-600 text-white font-bold py-2 px-4 rounded-lg shadow-md hover:bg-blue-700">Exportar a Word</button>
              </div>
            </div>
        </div>
      </div>
    </>
  )};

  const renderMatchesSection = () => (
    <>
      <div className="mb-8 border-t pt-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">{editingMatchId ? 'Editar Partido' : 'Añadir Partido'}</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <input type="text" name="rival" value={newMatch.rival} onChange={handleMatchChange} placeholder="Rival" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"/>
          <input type="date" name="fecha" value={newMatch.fecha} onChange={handleMatchChange} className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"/>
          <input type="text" name="lugar" value={newMatch.lugar} onChange={handleMatchChange} placeholder="Lugar" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"/>
          <input type="time" name="hora" value={newMatch.hora} onChange={handleMatchChange} className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"/>
          <input type="text" name="resultado" value={newMatch.resultado} onChange={handleMatchChange} placeholder="Resultado (Ej: 2-1)" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"/>
          <input type="text" name="sistemaUtilizado" value={newMatch.sistemaUtilizado} onChange={handleMatchChange} placeholder="Sistema Utilizado (Ej: 4-3-3)" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"/>
          <textarea name="titulares" value={newMatch.titulares} onChange={handleMatchChange} placeholder="Jugadores Titulares (uno por línea, separados por coma)" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" rows="4"></textarea>
          <textarea name="suplentes" value={newMatch.suplentes} onChange={handleMatchChange} placeholder="Jugadores Suplentes (uno por línea, separados por coma)" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2" rows="3"></textarea>
          
          <div className="col-span-full border rounded-lg p-4 bg-gray-50">
            <h4 className="text-lg font-semibold text-gray-700 mb-2">Eventos del Partido</h4>
            <div className="flex gap-2 mb-4 items-end">
              <select value={newEvent.player} onChange={(e) => setNewEvent({...newEvent, player: e.target.value})} className="flex-1 p-2 border rounded-lg">
                <option value="">Seleccionar Jugador</option>
                {teamMembers.map(m => <option key={m.id} value={m.fullName}>{m.fullName}</option>)}
              </select>
              <select value={newEvent.type} onChange={(e) => setNewEvent({...newEvent, type: e.target.value})} className="flex-1 p-2 border rounded-lg">
                <option value="">Seleccionar Evento</option>
                {eventTypes.map(e => <option key={e.value} value={e.value}>{e.label}</option>)}
              </select>
              {newEvent.type === 'lesion' && (
                <input type="text" value={newEvent.detail} onChange={(e) => setNewEvent({...newEvent, detail: e.target.value})} placeholder="Detalle (ej: tobillo)" className="flex-1 p-2 border rounded-lg"/>
              )}
              <button onClick={addEventToMatch} className="bg-blue-500 text-white font-bold py-2 px-4 rounded-lg shadow-md hover:bg-blue-600">Añadir</button>
            </div>
            <ul className="space-y-2">
              {newMatch.events.map((event, index) => (
                <li key={index} className="flex justify-between items-center bg-white p-2 rounded">
                  <span>{event.player} - {eventTypes.find(e=>e.value === event.type)?.label} {event.detail && `(${event.detail})`}</span>
                  <button onClick={() => removeEventFromMatch(index)} className="text-red-500 hover:text-red-700 font-bold">X</button>
                </li>
              ))}
            </ul>
          </div>

          <div className="col-span-1 sm:col-span-2 border-t pt-4 mt-4">
            <h4 className="text-lg font-semibold text-gray-700 mb-2">Observaciones del Partido</h4>
            <textarea value={newMatch.observaciones.organizacionOfensiva} onChange={(e) => handleMatchObservacionesChange('organizacionOfensiva', e.target.value)} placeholder="Organización Ofensiva" className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 mb-2" rows="3"></textarea>
            <textarea value={newMatch.observaciones.organizacionDefensiva} onChange={(e) => handleMatchObservacionesChange('organizacionDefensiva', e.target.value)} placeholder="Organización Defensiva" className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 mb-2" rows="3"></textarea>
            <textarea value={newMatch.observaciones.transicionOfensiva} onChange={(e) => handleMatchObservacionesChange('transicionOfensiva', e.target.value)} placeholder="Transición Ofensiva" className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 mb-2" rows="3"></textarea>
            <textarea value={newMatch.observaciones.transicionDefensiva} onChange={(e) => handleMatchObservacionesChange('transicionDefensiva', e.target.value)} placeholder="Transición Defensiva" className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 mb-2" rows="3"></textarea>
            <textarea value={newMatch.observaciones.abpOfensivo} onChange={(e) => handleMatchObservacionesChange('abpOfensivo', e.target.value)} placeholder="ABP Ofensivo" className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 mb-2" rows="3"></textarea>
            <textarea value={newMatch.observaciones.abpDefensivo} onChange={(e) => handleMatchObservacionesChange('abpDefensivo', e.target.value)} placeholder="ABP Defensivo" className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 mb-2" rows="3"></textarea>
            <textarea value={newMatch.observaciones.notasAdicionales} onChange={(e) => handleMatchObservacionesChange('notasAdicionales', e.target.value)} placeholder="Notas Adicionales" className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" rows="3"></textarea>
          </div>
          
          <input type="url" name="enlaceVideo" value={newMatch.enlaceVideo} onChange={handleMatchChange} placeholder="Enlace de Video del Partido" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 sm:col-span-2"/>
          
          <div className="col-span-1 sm:col-span-2 flex gap-2">
            <button onClick={addOrUpdateMatch} className="flex-1 bg-green-600 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-green-700 transition-all">
              {editingMatchId ? 'Guardar Cambios' : 'Guardar Partido'}
            </button>
            {editingMatchId && (
              <button onClick={cancelEditingMatch} className="bg-gray-400 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-gray-500">
                Cancelar
              </button>
            )}
          </div>
        </div>
      </div>
      <div>
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Partidos Guardados</h2>
        <ul className="space-y-4">
          {matches.map(match => (
            <li key={match.id} className="bg-white p-4 rounded-lg shadow-sm border">
              <div className="flex flex-col sm:flex-row justify-between">
                <div className="flex-1">
                  <p className="font-bold text-lg">vs {match.rival} <span className="font-normal text-base text-gray-600">({match.resultado})</span></p>
                  <p className="text-sm text-gray-500">{match.fecha} - {match.lugar}</p>
                </div>
                <div className="flex items-center gap-2 mt-4 sm:mt-0 justify-end">
                  <button onClick={() => setViewingMatch(match)} className="bg-blue-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-blue-600">Ver</button>
                  <button onClick={() => startEditingMatch(match)} className="bg-yellow-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-yellow-600">Editar</button>
                  <button onClick={() => deleteMatch(match.id)} className="bg-red-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-red-600">Eliminar</button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </>
  );
  
  const renderScoutingSection = () => {
    const handleExportScoutingExcel = () => {
      const dataToExport = scoutingReports.map(r => ({
        'Nombre Jugador': r.nombreJugador,
        'Fecha Nacimiento': r.fechaNacimiento,
        'Edad': r.edad,
        'Club': r.club,
        'Posición Principal': r.posicionPrincipal,
        'Fortalezas - Técnica': r.fortalezas?.tecnica,
        'Fortalezas - Táctica Ind.': r.fortalezas?.tacticaIndividual,
        'Fortalezas - Táctica Colectiva Ofensiva': r.fortalezas?.tacticaColectivaOfensiva,
        'Fortalezas - Táctica Colectiva Defensiva': r.fortalezas?.tacticaColectivaDefensiva,
        'Fortalezas - Juego Aéreo': r.fortalezas?.juegoAereo,
        'Fortalezas - Comunicación': r.fortalezas?.comunicacion,
        'Fortalezas - Actitudes': r.fortalezas?.actitudes,
        'Fortalezas - Físico': r.fortalezas?.fisico,
        'Fortalezas - Tiro Libres': r.fortalezas?.tiroLibres,
        'Fortalezas - Penales': r.fortalezas?.penales,
        'Debilidades - Técnica': r.debilidades?.tecnica,
        'Debilidades - Táctica Ind.': r.debilidades?.tacticaIndividual,
        'Debilidades - Táctica Colectiva Ofensiva': r.debilidades?.tacticaColectivaOfensiva,
        'Debilidades - Táctica Colectiva Defensiva': r.debilidades?.tacticaColectivaDefensiva,
        'Debilidades - Juego Aéreo': r.debilidades?.juegoAereo,
        'Debilidades - Comunicación': r.debilidades?.comunicacion,
        'Debilidades - Actitudes': r.debilidades?.actitudes,
        'Debilidades - Físico': r.debilidades?.fisico,
        'Debilidades - Tiro Libres': r.debilidades?.tiroLibres,
        'Debilidades - Penales': r.debilidades?.penales,
        'Historial Lesiones': r.historialLesiones,
        'Notas Adicionales': r.notasAdicionales,
      }));
      exportToExcel(dataToExport, 'Scouting');
    };

    const handleExportScoutingWord = () => {
      if (typeof docx === 'undefined') return;
      const { Document, Packer, Paragraph, HeadingLevel, TextRun } = docx;

      const children = scoutingReports.flatMap(r => [
        new Paragraph({ text: `Informe de Scouting: ${r.nombreJugador}`, heading: HeadingLevel.HEADING_1, spacing: { before: 300 } }),
        new Paragraph({ children: [new TextRun({ text: "Club: ", bold: true }), new TextRun(r.club || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Posición: ", bold: true }), new TextRun(r.posicionPrincipal || '')] }),
        new Paragraph({ text: "Fortalezas", heading: HeadingLevel.HEADING_2, spacing: { before: 200 } }),
        new Paragraph({ children: [new TextRun({ text: "Técnica: ", bold: true }), new TextRun(r.fortalezas?.tecnica || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Táctica Individual: ", bold: true }), new TextRun(r.fortalezas?.tacticaIndividual || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Táctica Colectiva Ofensiva: ", bold: true }), new TextRun(r.fortalezas?.tacticaColectivaOfensiva || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Táctica Colectiva Defensiva: ", bold: true }), new TextRun(r.fortalezas?.tacticaColectivaDefensiva || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Juego Aéreo: ", bold: true }), new TextRun(r.fortalezas?.juegoAereo || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Comunicación: ", bold: true }), new TextRun(r.fortalezas?.comunicacion || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Actitudes: ", bold: true }), new TextRun(r.fortalezas?.actitudes || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Físico: ", bold: true }), new TextRun(r.fortalezas?.fisico || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Tiro Libres: ", bold: true }), new TextRun(r.fortalezas?.tiroLibres || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Penales: ", bold: true }), new TextRun(r.fortalezas?.penales || '')] }),
        new Paragraph({ text: "Debilidades", heading: HeadingLevel.HEADING_2, spacing: { before: 200 } }),
        new Paragraph({ children: [new TextRun({ text: "Técnica: ", bold: true }), new TextRun(r.debilidades?.tecnica || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Táctica Individual: ", bold: true }), new TextRun(r.debilidades?.tacticaIndividual || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Táctica Colectiva Ofensiva: ", bold: true }), new TextRun(r.debilidades?.tacticaColectivaOfensiva || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Táctica Colectiva Defensiva: ", bold: true }), new TextRun(r.debilidades?.tacticaColectivaDefensiva || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Juego Aéreo: ", bold: true }), new TextRun(r.debilidades?.juegoAereo || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Comunicación: ", bold: true }), new TextRun(r.debilidades?.comunicacion || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Actitudes: ", bold: true }), new TextRun(r.debilidades?.actitudes || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Físico: ", bold: true }), new TextRun(r.debilidades?.fisico || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Tiro Libres: ", bold: true }), new TextRun(r.debilidades?.tiroLibres || '')] }),
        new Paragraph({ children: [new TextRun({ text: "Penales: ", bold: true }), new TextRun(r.debilidades?.penales || '')] }),
        new Paragraph({ text: "Historial de Lesiones", heading: HeadingLevel.HEADING_2, spacing: { before: 200 } }),
        new Paragraph(r.historialLesiones || ''),
        new Paragraph({ text: '', spacing: { after: 400 } }),
      ]);
      const doc = new Document({ sections: [{ children }] });
      exportToWord(doc, 'Scouting');
    };

    return (
      <>
        <div className="mb-8 border-t pt-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">{editingScoutingReportId ? 'Editar Informe de Scouting' : 'Añadir Informe de Scouting'}</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <input type="text" name="nombreJugador" value={newScoutingReport.nombreJugador} onChange={handleScoutingChange} placeholder="Nombre del Jugador" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"/>
            <input type="date" name="fechaNacimiento" value={newScoutingReport.fechaNacimiento} onChange={handleScoutingChange} className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"/>
            <input type="number" name="edad" value={newScoutingReport.edad} onChange={handleScoutingChange} placeholder="Edad" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" readOnly/>
            <input type="text" name="categoria" value={newScoutingReport.categoria} onChange={handleScoutingChange} placeholder="Categoría" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"/>
            <input type="text" name="club" value={newScoutingReport.club} onChange={handleScoutingChange} placeholder="Club Actual" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"/>
            <select name="posicionPrincipal" value={newScoutingReport.posicionPrincipal} onChange={handleScoutingChange} className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500">
              <option value="">Posición Principal</option>{positions.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
            <input type="text" name="posicionSecundaria" value={newScoutingReport.posicionSecundaria} onChange={handleScoutingChange} placeholder="Posición Secundaria" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"/>
            <select name="piernaHabil" value={newScoutingReport.piernaHabil} onChange={handleScoutingChange} className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500">
              <option value="">Pierna Hábil</option>{dominantLegs.map(l => <option key={l} value={l}>{l}</option>)}
            </select>
            <input type="number" name="talla" value={newScoutingReport.talla} onChange={handleScoutingChange} placeholder="Talla (cm)" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"/>
            <input type="number" name="peso" value={newScoutingReport.peso} onChange={handleScoutingChange} placeholder="Peso (kg)" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"/>
            <input type="date" name="fechaInforme" value={newScoutingReport.fechaInforme} onChange={handleScoutingChange} className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 col-span-1 lg:col-span-2"/>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            <div className="bg-green-50 p-4 rounded-lg border border-green-200">
              <h4 className="text-lg font-semibold text-green-800 mb-2">Fortalezas</h4>
              <div className="space-y-2">
                <ScoutingDetailInput category="fortalezas" field="tecnica" placeholder="Técnica" value={newScoutingReport.fortalezas.tecnica} handleNestedChange={handleNestedScoutingChange}/>
                <ScoutingDetailInput category="fortalezas" field="tacticaIndividual" placeholder="Táctica Individual" value={newScoutingReport.fortalezas.tacticaIndividual} handleNestedChange={handleNestedScoutingChange}/>
                <ScoutingDetailInput category="fortalezas" field="tacticaColectivaOfensiva" placeholder="Táctica Colectiva Ofensiva" value={newScoutingReport.fortalezas.tacticaColectivaOfensiva} handleNestedChange={handleNestedScoutingChange}/>
                <ScoutingDetailInput category="fortalezas" field="tacticaColectivaDefensiva" placeholder="Táctica Colectiva Defensiva" value={newScoutingReport.fortalezas.tacticaColectivaDefensiva} handleNestedChange={handleNestedScoutingChange}/>
                <ScoutingDetailInput category="fortalezas" field="juegoAereo" placeholder="Juego Aéreo" value={newScoutingReport.fortalezas.juegoAereo} handleNestedChange={handleNestedScoutingChange}/>
                <ScoutingDetailInput category="fortalezas" field="comunicacion" placeholder="Comunicación" value={newScoutingReport.fortalezas.comunicacion} handleNestedChange={handleNestedScoutingChange}/>
                <ScoutingDetailInput category="fortalezas" field="actitudes" placeholder="Actitudes" value={newScoutingReport.fortalezas.actitudes} handleNestedChange={handleNestedScoutingChange}/>
                <ScoutingDetailInput category="fortalezas" field="fisico" placeholder="Físico" value={newScoutingReport.fortalezas.fisico} handleNestedChange={handleNestedScoutingChange}/>
                <ScoutingDetailInput category="fortalezas" field="tiroLibres" placeholder="Tiro Libres" value={newScoutingReport.fortalezas.tiroLibres} handleNestedChange={handleNestedScoutingChange}/>
                <ScoutingDetailInput category="fortalezas" field="penales" placeholder="Penales" value={newScoutingReport.fortalezas.penales} handleNestedChange={handleNestedScoutingChange}/>
              </div>
            </div>
            <div className="bg-red-50 p-4 rounded-lg border border-red-200">
              <h4 className="text-lg font-semibold text-red-800 mb-2">Debilidades</h4>
              <div className="space-y-2">
                <ScoutingDetailInput category="debilidades" field="tecnica" placeholder="Técnica" value={newScoutingReport.debilidades.tecnica} handleNestedChange={handleNestedScoutingChange}/>
                <ScoutingDetailInput category="debilidades" field="tacticaIndividual" placeholder="Táctica Individual" value={newScoutingReport.debilidades.tacticaIndividual} handleNestedChange={handleNestedScoutingChange}/>
                <ScoutingDetailInput category="debilidades" field="tacticaColectivaOfensiva" placeholder="Táctica Colectiva Ofensiva" value={newScoutingReport.debilidades.tacticaColectivaOfensiva} handleNestedChange={handleNestedScoutingChange}/>
                <ScoutingDetailInput category="debilidades" field="tacticaColectivaDefensiva" placeholder="Táctica Colectiva Defensiva" value={newScoutingReport.debilidades.tacticaColectivaDefensiva} handleNestedChange={handleNestedScoutingChange}/>
                <ScoutingDetailInput category="debilidades" field="juegoAereo" placeholder="Juego Aéreo" value={newScoutingReport.debilidades.juegoAereo} handleNestedChange={handleNestedScoutingChange}/>
                <ScoutingDetailInput category="debilidades" field="comunicacion" placeholder="Comunicación" value={newScoutingReport.debilidades.comunicacion} handleNestedChange={handleNestedScoutingChange}/>
                <ScoutingDetailInput category="debilidades" field="actitudes" placeholder="Actitudes" value={newScoutingReport.debilidades.actitudes} handleNestedChange={handleNestedScoutingChange}/>
                <ScoutingDetailInput category="debilidades" field="fisico" placeholder="Físico" value={newScoutingReport.debilidades.fisico} handleNestedChange={handleNestedScoutingChange}/>
                <ScoutingDetailInput category="debilidades" field="tiroLibres" placeholder="Tiro Libres" value={newScoutingReport.debilidades.tiroLibres} handleNestedChange={handleNestedScoutingChange}/>
                <ScoutingDetailInput category="debilidades" field="penales" placeholder="Penales" value={newScoutingReport.debilidades.penales} handleNestedChange={handleNestedScoutingChange}/>
              </div>
            </div>
          </div>
          
          <textarea name="historialLesiones" value={newScoutingReport.historialLesiones} onChange={handleScoutingChange} placeholder="Historial de Lesiones" className="mt-6 w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" rows="4"></textarea>
          <textarea name="notasAdicionales" value={newScoutingReport.notasAdicionales} onChange={handleScoutingChange} placeholder="Notas Adicionales" className="mt-6 w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500" rows="4"></textarea>
          <input type="url" name="enlaceVideo" value={newScoutingReport.enlaceVideo} onChange={handleScoutingChange} placeholder="Enlace de Video" className="mt-4 w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"/>
          
          <div className="mt-6 flex gap-2">
            <button onClick={addOrUpdateScoutingReport} className="flex-1 bg-green-600 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-green-700 transition-all">
              {editingScoutingReportId ? 'Guardar Cambios' : 'Guardar Informe'}
            </button>
            {editingScoutingReportId && (
              <button onClick={cancelEditingScoutingReport} className="bg-gray-400 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-gray-500">
                Cancelar
              </button>
            )}
          </div>
        </div>
        <div>
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Informes Guardados</h2>
          {scoutingReports.length === 0 ? (<p className="text-gray-500 text-center py-8">¡Aún no hay informes de scouting!</p>) : (
          <>
          <ul className="space-y-4">
            {scoutingReports.map(report => (
              <li key={report.id} className="bg-white p-4 rounded-lg shadow-sm border">
                <div className="flex flex-col sm:flex-row justify-between">
                  <div className="flex-1">
                    <p className="font-bold text-lg">{report.nombreJugador} <span className="font-normal text-base text-gray-600">({report.club})</span></p>
                    <p className="text-sm text-gray-500">{report.posicionPrincipal} - Categoría {report.categoria}</p>
                  </div>
                  <div className="flex items-center gap-2 mt-4 sm:mt-0 justify-end">
                    <button onClick={() => setViewingScoutingReport(report)} className="bg-blue-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-blue-600">Ver</button>
                    <button onClick={() => startEditingScoutingReport(report)} className="bg-yellow-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-yellow-600">Editar</button>
                    <button onClick={() => deleteScoutingReport(report.id)} className="bg-red-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-red-600">Eliminar</button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
          <div className="mt-8 border-t pt-6 text-center">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">Opciones de Exportación</h3>
            <div className="flex justify-center gap-4">
              <button onClick={handleExportScoutingExcel} className="bg-green-600 text-white font-bold py-2 px-4 rounded-lg shadow-md hover:bg-green-700">Exportar a Excel</button>
              <button onClick={handleExportScoutingWord} className="bg-blue-600 text-white font-bold py-2 px-4 rounded-lg shadow-md hover:bg-blue-700">Exportar a Word</button>
            </div>
          </div>
          </>
          )}
        </div>
      </>
    );
  };
  
  const renderPlayerStatsSection = () => {
    const handleExportStatsExcel = () => {
      const dataToExport = teamMembers.map(member => {
        const stats = playerStats[member.fullName] || {};
        return {
          'Jugador': member.fullName,
          'Partidos Titular': stats.titular || 0,
          'Minutos Jugados': stats.minutosJugados || 0,
          'Goles': stats.goles || 0,
          'Goles de Cabeza': stats.golesDeCabeza || 0,
          'Goles de Tiro Libre': stats.golesDeTiroLibre || 0,
          'Goles de Penal': stats.golesDePenal || 0,
          'Asistencias': stats.asistencias || 0,
          'Tarjetas Amarillas': stats.tarjetasAmarillas || 0,
          'Tarjetas Rojas': stats.tarjetasRojas || 0,
          'Lesiones': stats.lesiones?.join(', ') || '',
        };
      });
      exportToExcel(dataToExport, 'Estadisticas_Jugadores');
    };

    const handleExportStatsWord = () => {
      if (typeof docx === 'undefined') return;
      const { Document, Packer, Paragraph, HeadingLevel, Table, TableRow, TableCell } = docx;

      const header = new TableRow({ children: [
        new TableCell({ children: [new Paragraph("Jugador")]}),
        new TableCell({ children: [new Paragraph("Titular")]}),
        new TableCell({ children: [new Paragraph("Min")]}),
        new TableCell({ children: [new Paragraph("Goles")]}),
        new TableCell({ children: [new Paragraph("Asist")]}),
        new TableCell({ children: [new Paragraph("T.A.")]}),
        new TableCell({ children: [new Paragraph("T.R.")]}),
      ]});

      const dataRows = teamMembers.map(member => {
        const stats = playerStats[member.fullName] || {};
        return new TableRow({ children: [
          new TableCell({ children: [new Paragraph(member.fullName)] }),
          new TableCell({ children: [new Paragraph(String(stats.titular || 0))] }),
          new TableCell({ children: [new Paragraph(String(stats.minutosJugados || 0))] }),
          new TableCell({ children: [new Paragraph(String(stats.goles || 0))] }),
          new TableCell({ children: [new Paragraph(String(stats.asistencias || 0))] }),
          new TableCell({ children: [new Paragraph(String(stats.tarjetasAmarillas || 0))] }),
          new TableCell({ children: [new Paragraph(String(stats.tarjetasRojas || 0))] }),
        ]});
      });

      const table = new Table({ rows: [header, ...dataRows] });
      const doc = new Document({ sections: [{ children: [
        new Paragraph({ text: 'Estadísticas de Jugadores', heading: HeadingLevel.HEADING_1 }),
        table
      ]}]});

      exportToWord(doc, 'Estadisticas_Jugadores');
    };

    return (
    <div className="mb-8 border-t pt-8">
      <h2 className="text-2xl font-semibold text-gray-800 mb-4">Estadísticas de Jugadores</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white rounded-lg shadow">
          <thead className="bg-gray-200">
            <tr>
              <th className="px-4 py-2 text-left">Jugador</th>
              <th className="px-4 py-2">Titular</th>
              <th className="px-4 py-2">Minutos</th>
              <th className="px-4 py-2">Goles</th>
              <th className="px-4 py-2">G. Cabeza</th>
              <th className="px-4 py-2">G. T. Libre</th>
              <th className="px-4 py-2">G. Penal</th>
              <th className="px-4 py-2">Asist.</th>
              <th className="px-4 py-2">T. Amar.</th>
              <th className="px-4 py-2">T. Rojas</th>
              <th className="px-4 py-2">Lesiones</th>
            </tr>
          </thead>
          <tbody>
            {teamMembers.map(member => (
              <tr key={member.id} className="border-b">
                <td className="px-4 py-2 font-semibold">{member.fullName}</td>
                <td className="px-4 py-2 text-center">{playerStats[member.fullName]?.titular || 0}</td>
                <td className="px-4 py-2 text-center">{playerStats[member.fullName]?.minutosJugados || 0}</td>
                <td className="px-4 py-2 text-center">{playerStats[member.fullName]?.goles || 0}</td>
                <td className="px-4 py-2 text-center">{playerStats[member.fullName]?.golesDeCabeza || 0}</td>
                <td className="px-4 py-2 text-center">{playerStats[member.fullName]?.golesDeTiroLibre || 0}</td>
                <td className="px-4 py-2 text-center">{playerStats[member.fullName]?.golesDePenal || 0}</td>
                <td className="px-4 py-2 text-center">{playerStats[member.fullName]?.asistencias || 0}</td>
                <td className="px-4 py-2 text-center">{playerStats[member.fullName]?.tarjetasAmarillas || 0}</td>
                <td className="px-4 py-2 text-center">{playerStats[member.fullName]?.tarjetasRojas || 0}</td>
                <td className="px-4 py-2 text-center">{playerStats[member.fullName]?.lesiones.join(', ') || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-8 border-t pt-6 text-center">
        <h3 className="text-lg font-semibold text-gray-700 mb-4">Opciones de Exportación</h3>
        <div className="flex justify-center gap-4">
          <button onClick={handleExportStatsExcel} className="bg-green-600 text-white font-bold py-2 px-4 rounded-lg shadow-md hover:bg-green-700">Exportar a Excel</button>
          <button onClick={handleExportStatsWord} className="bg-blue-600 text-white font-bold py-2 px-4 rounded-lg shadow-md hover:bg-blue-700">Exportar a Word</button>
        </div>
      </div>
    </div>
  )};

  const renderMatchVideosSection = () => (
    <>
      <div className="mb-8 border-t pt-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Videos de Partidos</h2>
        <div className="flex justify-center mb-6">
          <button
            onClick={() => setActiveMatchVideoSection('myTeamMatches')}
            className={`py-2 px-4 rounded-l-full font-bold transition-all duration-300 ${activeMatchVideoSection === 'myTeamMatches' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}
          >
            Partidos de mi equipo
          </button>
          <button
            onClick={() => setActiveMatchVideoSection('rivalTeamMatches')}
            className={`py-2 px-4 font-bold transition-all duration-300 ${activeMatchVideoSection === 'rivalTeamMatches' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}
          >
            Partidos de equipos rivales
          </button>
          <button
            onClick={() => setActiveMatchVideoSection('others')}
            className={`py-2 px-4 rounded-r-full font-bold transition-all duration-300 ${activeMatchVideoSection === 'others' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}
          >
            Otros
          </button>
        </div>
        
        <div className="bg-gray-50 p-6 rounded-xl shadow-lg mb-8">
            <h3 className="text-xl font-bold mb-4 text-center">{editingMatchVideo ? 'Editar Video de Partido' : 'Añadir Nuevo Video de Partido'}</h3>
            <div className="grid grid-cols-1 gap-4">
                <input type="text" name="teams" value={newMatchVideo.teams} onChange={handleMatchVideoChange} placeholder="Equipos (Ej: Equipo A vs Equipo B)" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"/>
                <input type="url" name="link" value={newMatchVideo.link} onChange={handleMatchVideoChange} placeholder="Enlace del video" className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"/>
                <div className="flex gap-2">
                  <button onClick={addOrUpdateMatchVideo} className="flex-1 bg-green-600 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-green-700 transition-all">
                    {editingMatchVideo ? 'Guardar Cambios' : 'Guardar Video'}
                  </button>
                  {editingMatchVideo && (
                    <button onClick={cancelEditingMatchVideo} className="bg-gray-400 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-gray-500">
                      Cancelar
                    </button>
                  )}
                </div>
            </div>
        </div>

        <div>
            <h3 className="text-xl md:text-2xl font-bold text-center text-gray-800 mb-6">
              Videos Guardados
            </h3>
            <ul className="space-y-4">
              {matchVideos[activeMatchVideoSection].map(video => (
                <li key={video.id} className="bg-white p-4 rounded-lg shadow-sm border">
                  <div className="flex flex-col sm:flex-row justify-between">
                    <div className="flex-1">
                      <p className="font-bold text-lg">{video.teams}</p>
                      <a href={video.link} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:underline break-all">{video.link}</a>
                    </div>
                    <div className="flex items-center gap-2 mt-4 sm:mt-0 justify-end">
                      <button onClick={() => startEditingMatchVideo(video)} className="bg-yellow-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-yellow-600">Editar</button>
                      <button onClick={() => deleteMatchVideo(video.id)} className="bg-red-500 text-white py-2 px-4 rounded-lg shadow-md hover:bg-red-600">Eliminar</button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
        </div>
      </div>
    </>
  );

  return (
    <div className="min-h-screen bg-gray-100 p-4 sm:p-8 font-[Inter] relative">
      <div className="absolute top-4 left-4 text-gray-700 font-bold text-lg">
        Iván Sánchez
      </div>
      <div className="max-w-4xl w-full bg-white rounded-xl shadow-lg p-6 sm:p-8 mx-auto">
        <h1 className="text-3xl sm:text-4xl font-extrabold text-gray-900 mb-2 text-center">Gestor de Equipo</h1>
        <p className="text-sm text-gray-600 text-center mb-8">ID de Usuario: <span className="font-mono text-xs bg-gray-200 px-2 py-1 rounded-md">{userId}</span></p>
        
        <div className="flex flex-wrap justify-center gap-4 mb-8">
          <button onClick={() => setCurrentSection('gestion')} className={`px-6 py-3 rounded-lg font-bold transition-colors ${currentSection === 'gestion' ? 'bg-blue-600 text-white shadow-lg' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}>Gestión</button>
          <button onClick={() => setCurrentSection('members')} className={`px-6 py-3 rounded-lg font-bold transition-colors ${currentSection === 'members' ? 'bg-blue-600 text-white shadow-lg' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}>Miembros</button>
          <button onClick={() => setCurrentSection('trainings')} className={`px-6 py-3 rounded-lg font-bold transition-colors ${currentSection === 'trainings' ? 'bg-blue-600 text-white shadow-lg' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}>Entrenamientos</button>
          <button onClick={() => setCurrentSection('attendance')} className={`px-6 py-3 rounded-lg font-bold transition-colors ${currentSection === 'attendance' ? 'bg-blue-600 text-white shadow-lg' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}>Asistencia</button>
          <button onClick={() => setCurrentSection('playerStats')} className={`px-6 py-3 rounded-lg font-bold transition-colors ${currentSection === 'playerStats' ? 'bg-blue-600 text-white shadow-lg' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}>Estadísticas</button>
          <button onClick={() => setCurrentSection('principles')} className={`px-6 py-3 rounded-lg font-bold transition-colors ${currentSection === 'principles' ? 'bg-blue-600 text-white shadow-lg' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}>Principios Tácticos</button>
          <button onClick={() => setCurrentSection('match-plans')} className={`px-6 py-3 rounded-lg font-bold transition-colors ${currentSection === 'match-plans' ? 'bg-blue-600 text-white shadow-lg' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}>Planes de Partidos</button>
          <button onClick={() => setCurrentSection('matches')} className={`px-6 py-3 rounded-lg font-bold transition-colors ${currentSection === 'matches' ? 'bg-blue-600 text-white shadow-lg' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}>Partidos</button>
          <button onClick={() => setCurrentSection('scouting')} className={`px-6 py-3 rounded-lg font-bold transition-colors ${currentSection === 'scouting' ? 'bg-blue-600 text-white shadow-lg' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}>Scouting</button>
          <button onClick={() => setCurrentSection('videos')} className={`px-6 py-3 rounded-lg font-bold transition-colors ${currentSection === 'videos' ? 'bg-blue-600 text-white shadow-lg' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}>Videos Entrenamiento</button>
          <button onClick={() => setCurrentSection('matchVideos')} className={`px-6 py-3 rounded-lg font-bold transition-colors ${currentSection === 'matchVideos' ? 'bg-blue-600 text-white shadow-lg' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}>Videos de Partidos</button>
          <button onClick={() => setCurrentSection('videoAnalysis')} className={`px-6 py-3 rounded-lg font-bold transition-colors ${currentSection === 'videoAnalysis' ? 'bg-blue-600 text-white shadow-lg' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}>Video Análisis</button>
        </div>

        {currentSection === 'gestion' && renderGestionSection()}
        
        {(selectedTeamId && selectedSeasonId && currentSection !== 'gestion') ? (
          <>
            {currentSection === 'members' && renderMembersSection()}
            {currentSection === 'trainings' && renderTrainingsSection()}
            {currentSection === 'attendance' && renderAttendanceSection()}
            {currentSection === 'playerStats' && renderPlayerStatsSection()}
            {currentSection === 'principles' && renderTacticalPrinciplesSection()}
            {currentSection === 'match-plans' && renderMatchPlansSection()}
            {currentSection === 'matches' && renderMatchesSection()}
            {currentSection === 'scouting' && renderScoutingSection()}
            {currentSection === 'videos' && renderVideosSection()}
            {currentSection === 'videoAnalysis' && renderVideoAnalysisSection()}
            {currentSection === 'matchVideos' && renderMatchVideosSection()}
          </>
        ) : currentSection !== 'gestion' && (
          <div className="text-center p-8 bg-gray-50 rounded-lg">
            <p className="text-gray-600">Por favor, ve a la sección "Gestión" para seleccionar o crear un equipo y una temporada.</p>
          </div>
        )}

      </div>
      {renderMemberDetailsModal()}
      {renderTrainingDetailsModal()}
      {renderAnalysisDetailsModal()}
      {renderMatchDetailsModal()}
      {renderScoutingReportDetailsModal()}
    </div>
  );
};

export default App;
