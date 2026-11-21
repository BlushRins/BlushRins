<picture>
  <source media="(max-width: 640px) and (prefers-reduced-motion: reduce)" srcset="https://raw.githubusercontent.com/BlushRins/BlushRins/main/assets/introduction-mobile-still.png">
  <source media="(max-width: 640px)" srcset="https://raw.githubusercontent.com/BlushRins/BlushRins/main/assets/introduction-mobile-loop.png">
  <source media="(prefers-reduced-motion: reduce)" srcset="https://raw.githubusercontent.com/BlushRins/BlushRins/main/assets/introduction-still.png">
  <img src="./assets/introduction-loop.png" width="1000" alt="Hi, I’m Matthew Llenos. I go by BlushRins, and I’m an aspiring software developer.">
</picture>

<h2 align="center">Matthew Llenos</h2>

<p align="center"><strong>Aspiring software developer</strong><br><code>C data structures / offline web apps / study tools</code></p>

<p align="center">
  <a href="https://www.instagram.com/44_matteo_mat/"><img src="./assets/profile-card/instagram.svg" alt="Instagram — @44_matteo_mat" height="32"></a>
  <a href="#on-my-workbench"><img src="./assets/profile-card/projects.svg" alt="Explore my projects" height="32"></a>
</p>

## About me

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="https://raw.githubusercontent.com/BlushRins/BlushRins/main/assets/profile-card/terminal-still.png">
  <img src="./assets/profile-card/terminal-dance-loop.png" width="132" align="right" alt="My rose-colored pixel-B terminal doing a two-step">
</picture>

I go by **BlushRins** online. Two things I keep track of are what I lifted last week and what I learned in class. That’s where Lift Tracker and Study Hub started.

I’m learning C by working through data structures. In a linked list, each node holds a value and a pointer. Following those pointers lets me read the whole list.

```c
for (const struct Node *node = head; node != NULL; node = node->next) {
    printf("%d\n", node->value);
}
```

<p>
  <img src="./assets/linked-list.svg" width="720" alt="Animated 4-node C linked list traversal from head through nodes 12, 27, 44, and 58 to NULL">
</p>

[See how the nodes connect](https://github.com/BlushRins/obsidian-study-vault/blob/HEAD/notes/linked-list-nodes.md)

Here is where I am in the course. Each checkpoint links to the next, like the nodes above.

<p>
  <img src="./assets/roadmap.svg" width="720" alt="C data structures roadmap: bit vector and linked list are done, stack is up next, then queue, hash table, and tree">
</p>

## Right now

<p>
  <img src="./assets/now-card.svg" width="560" alt="Terminal card: learning C data structures, building camera-trackers, tracking lifts and class notes">
</p>

## Languages on my keyboard

Pick a key to explore the code. The PHP key opens the official manual.

<p>
  <a href="https://github.com/BlushRins/obsidian-study-vault/blob/HEAD/notes/linked-list-nodes.md"><img src="./assets/keycaps/c.svg" width="76" alt="C — Walk a linked list in C"></a>
  <a href="https://github.com/BlushRins/EmployeeProject_Llenos/blob/HEAD/src/version3/HourlyEmployee.java"><img src="./assets/keycaps/java.svg" width="76" alt="Java — Read the Java HourlyEmployee class"></a>
  <a href="https://www.php.net/manual/en/language.oop5.basic.php"><img src="./assets/keycaps/php.svg" width="76" alt="PHP — Explore PHP classes in the official manual"></a>
  <a href="https://github.com/BlushRins/obsidian-study-vault/blob/HEAD/.githooks/pre-commit"><img src="./assets/keycaps/shell.svg" width="76" alt="Shell — Read the shell pre-commit hook"></a>
  <a href="https://github.com/BlushRins/millennium-command-center-site/blob/HEAD/index.html"><img src="./assets/keycaps/html.svg" width="76" alt="HTML — Read the command center HTML"></a>
  <a href="https://github.com/BlushRins/millennium-command-center-site/blob/HEAD/style.css"><img src="./assets/keycaps/css.svg" width="76" alt="CSS — Read the command center stylesheet"></a>
  <a href="https://github.com/BlushRins/lift-tracker/blob/HEAD/sw.js"><img src="./assets/keycaps/javascript.svg" width="76" alt="JavaScript — Read the Lift Tracker service worker in JavaScript"></a>
  <a href="https://github.com/BlushRins/Studyhub/blob/HEAD/components/note/NoteViewer.tsx"><img src="./assets/keycaps/typescript.svg" width="76" alt="TypeScript — Read the Study Hub Markdown reader in TypeScript"></a>
</p>

## On my workbench

### <img src="./assets/bridge.svg" alt="" width="52" height="44" align="middle"> SignBridge

I want a conversation to work both ways between someone who signs and someone who speaks. SignBridge is the web app I’m building for that: signs and gestures become speech, and speech becomes live captions.

**Status: in progress.** The repository is still a stub, so the card below is a sketch of the idea, not a screenshot.

<p>
  <img src="./assets/workbench/signbridge-card.svg" width="720" alt="SignBridge concept sketch: an open hand becomes the spoken word Hello, and speech becomes live captions">
</p>

<p>
  <a href="https://github.com/BlushRins/SignBridge"><img src="./assets/workbench/btn-view-source.svg" alt="SignBridge repository on GitHub" height="32"></a>
</p>

### <img src="./assets/camera.svg" alt="" width="52" height="44" align="middle"> Camera trackers

I wanted my webcam to do something fun. Camera trackers shows a mirrored webcam in a resizable window. Hold a gesture, like a thumbs up, and it loops that gesture’s track and shows its picture on the opposite side. The camera feed is processed locally.

**Try it.** On Linux with a webcam, run `.venv/bin/python -m camera_trackers` and hold a thumbs up for about 0.2 seconds. Lower your hand out of view to stop the music.

<p>
  <img src="./assets/workbench/camera-trackers-card.svg" width="720" alt="Camera trackers sketch: a mirrored webcam view with a green thumbs-up outline loops a track and shows a picture on the opposite side">
</p>

<p>
  <a href="https://github.com/BlushRins/camera-trackers"><img src="./assets/workbench/btn-view-source.svg" alt="View camera trackers source on GitHub" height="32"></a>
</p>

### <img src="./assets/weight-plates.svg" alt="" width="52" height="44" align="middle"> Lift Tracker

Between sets, I want to know what I lifted last time and what to aim for next. Lift Tracker keeps both on one screen, logs sets offline, and saves the history on my phone.

**20-second demo.** Open Lift Tracker, pick **Squat**, enter **20 kg** and **5 reps**, then tap **Log set 1**. Refresh and look under **Today** for the set you just saved.

<p>
  <img src="./assets/workbench/lift-tracker-card.svg" width="720" alt="Lift Tracker sample logged set: Squat, 20 kg times 5 reps, saved offline">
</p>

<p>
  <a href="https://blushrins.github.io/lift-tracker/"><img src="./assets/workbench/btn-lift-tracker.svg" alt="Open Lift Tracker" height="32"></a>
  <a href="https://github.com/BlushRins/lift-tracker"><img src="./assets/workbench/btn-view-source.svg" alt="View Lift Tracker source on GitHub" height="32"></a>
</p>

### <img src="./assets/notebook.svg" alt="" width="52" height="44" align="middle"> Study Hub

I keep my data structures notes in Obsidian. Study Hub turns the same Markdown files into a web reader with code examples and diagrams. My bit-vector notes show how eight yes-or-no answers fit into a single byte.

**One-byte challenge.** If the rightmost bit represents 0, which numbers belong to the set `0b00101100`?

<p>
  <img src="./assets/workbench/bit-vector-byte.svg" width="720" alt="8-bit byte visualizer showing 0b00101100 with glowing pastel-pink 1 bits">
</p>

<details>
<summary>Check your answer</summary>

`{2, 3, 5}`. Count positions from the right, starting at 0. The three ones sit at positions 2, 3, and 5.

</details>

<p>
  <a href="https://github.com/BlushRins/Studyhub/blob/HEAD/content/Bit-Vector%20Sets.md#1-the-core-idea"><img src="./assets/workbench/btn-bit-vector.svg" alt="Explore the bit-vector notes" height="32"></a>
  <a href="https://github.com/BlushRins/Studyhub"><img src="./assets/workbench/btn-view-source.svg" alt="View Study Hub source on GitHub" height="32"></a>
</p>

## Contribution trail

My past year on GitHub

![Past-year totals for contributions, active days, commits, and pull requests](https://raw.githubusercontent.com/BlushRins/BlushRins/contribution-art/stats.svg)

<picture>
  <source media="(prefers-reduced-motion: no-preference)" srcset="https://raw.githubusercontent.com/BlushRins/BlushRins/contribution-art/snake.svg">
  <img src="https://raw.githubusercontent.com/BlushRins/BlushRins/contribution-art/calendar.svg" width="1000" alt="My GitHub contribution calendar for the past year. Brighter pink squares mark more active days.">
</picture>

<p align="center">
  <img src="./assets/footer.svg" width="720" alt="Thanks for stopping by">
</p>

<p align="center">
  <a href="https://www.instagram.com/44_matteo_mat/"><img src="./assets/profile-card/instagram.svg" alt="Instagram — @44_matteo_mat" height="32"></a>
  <a href="#"><img src="./assets/workbench/btn-back-to-top.svg" alt="Back to top" height="32"></a>
</p>
