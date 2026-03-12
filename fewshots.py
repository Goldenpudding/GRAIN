TASK_DECOMPOSITION_EXAMPLES =  """Question: In a dance class of 20 students, 20% enrolled in contemporary dance, 25% of the remaining enrolled in jazzdance, and the rest enrolled in hip-hop dance. What percentage of the entire students enrolled in hip-hopdance?
Plan:
Step 1: Calculate the total number of students who enrolled in contemporary and jazz dance.
Step 2: Calculate the total number of students who enrolled in hip-hop dance.
Step 3: Calculate the percentage of students who enrolledin hip-hop dance.

Question: Which actor won an Academy Award for his role as a boxer in the 1976 film, which was directed by John G. Avildsen?
Plan:
Step 1: Identify the 1976 film directed by John G. Avildsen.
Step 2: Determine if the film features a boxer as a character.
Step 3: Identify the actor who portrayed the boxer in this film.
Step 4: Check if this actor won an Academy Award for this role.

Question: What is the name of the philosopher who developed the theory of idealism and influenced the German Romantic movement, who was born in 1770?
Plan:
Step 1: Identify philosophers associated with idealism.
Step 2: Determine which of these philosophers influenced the German Romantic movement.
Step 3: Verify the birth year of these philosophers to find who was born in 1770.

Question: Which French scientist is known for his work on radioactivity and won two Nobel Prizes, one in Physics and one in Chemistry?
Plan:
Step 1: Identify scientists known for their work on radioactivity.
Step 2: Determine which of these scientists are French.
Step 3: Check which of these French scientists have won two Nobel Prizes, one in Physics and one in Chemistry.
Step 4: Confirm the scientist's name."""


TASK_REVISION_EXAMPLES = """Question: Which country was the first to grant women the right to vote in national elections, and in what year did this happen?
Previous Plan: 
Step 1: List all countries that currently have women's voting rights.
Step 2: Arrange these countries in alphabetical order.
Step 3: Select the first country on the list as the first to grant women's voting rights and note the year.
Knowledge:
Before the 18th century, women in all countries had almost no political rights. The women's suffrage movement was first proposed by Mary Wollstonecraft in 1792 in her book In Defense of Women's Rights. From the beginning of the 19th century, there were first calls in Britain for women to be given the right to vote and to give them the opportunity to participate in politics, even if it was for show. In the mid-19th century, the United States launched the women's suffrage movement, the first of which was held in Seneca Forsel, New York, in 1848. In the second half of the 19th century, the women's suffrage movement grew in Britain, the United States, New Zealand and other countries. In 1893, New Zealand became the first country in the world to recognise women's suffrage.
Thought: 
The previous plan uses alphabetical order, which doesn't reflect the actual timeline of when countries granted women the right to vote. To accurately identify the first country and the year it happened, it's essential to arrange the countries chronologically. Therefore, the revised plan adopts a timeline-based approach.
Revised Plan:
Step 1: Identify countries that granted women the right to vote in national elections.
Step 2: Determine the chronological order in which these countries granted women suffrage.
Step 3: Confirm which country was the first to enact this change and the corresponding year.
"""


TASK_SOLUTION_EXAMPLES = """Question: In a dance class of 20 students, 20% enrolled in contemporary dance, 25% of the remaining enrolled in jazzdance, and the rest enrolled in hip-hop dance. What percentage of the entire students enrolled in hip-hopdance?
Plan:
Step 1: Calculate the total number of students who enrolled in contemporary and jazz dance.
Step 2: Calculate the total number of students who enrolled in hip-hop dance.
Step 3: Calculate the percentage of students who enrolledin hip-hop dance.
Solution:
Step 1: 20% of 20 students is 4 students. 25% of the remaining 16 students is 4 students. So, a total of 8 students enrolled in contemporary and jazz dance.
Step 2: The remaining 12 students enrolled in hip-hop dance.
Step 3: The percentage of students who enrolled in hip-hop dance is 12/20=60%.
Finish[60%]
"""